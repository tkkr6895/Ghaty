"""Download Core Stack GeoServer layers for offline field use.

Goal
- Download *everything available* in Core Stack GeoServer for selected districts
  (vectors via WFS + rasters via WCS) so field validation can happen offline.

Why this script exists
- The Core Stack API `/get_generated_layer_urls/` can fail for some districts
  (e.g., Dakshina Kannada returning: DistrictSOI matching query does not exist).
- GeoServer still publishes layers; we can discover them via GetCapabilities.

What it does
- Fetch WFS GetCapabilities once, parse all feature `typeName`s.
- Fetch WCS GetCapabilities once (optional), parse all `CoverageId`s.
- Filter by regex patterns (e.g., `dakshina_kannada_`, `chikkamagaluru_`).
- Download:
  - vectors as GeoJSON (WFS GetFeature outputFormat=application/json)
  - vectors as KML (WFS GetFeature outputFormat=application/vnd.google-earth.kml+xml)
  - rasters as GeoTIFF (WCS GetCoverage format=geotiff)

Outputs
- outputs/corestack_offline_pack/
  - <pack_name>/
    - vectors_geojson/
    - vectors_kml/
    - rasters_geotiff/
    - manifest.csv
    - README.md

Usage
- python download_corestack_offline_pack.py --pack-name dk_chik \
    --pattern dakshina_kannada_ --pattern chikmagalur_ --pattern chikkamagaluru_

Notes
- Port 8443 must be reachable at download time. After download, you are offline.
- GeoTIFF rasters won’t render directly in Google Earth Pro; use QGIS offline.
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests
from requests import Response
from requests.exceptions import ChunkedEncodingError, ConnectionError, ReadTimeout


WORKSPACE_ROOT = Path(__file__).resolve().parent
OUT_ROOT = WORKSPACE_ROOT / "outputs" / "corestack_offline_pack"

DEFAULT_GEOSERVER_BASE = "https://geoserver.core-stack.org:8443/geoserver"
DEFAULT_WFS_VERSION = "1.0.0"
DEFAULT_WCS_VERSION = "2.0.1"


@dataclass(frozen=True)
class DownloadItem:
    kind: str  # vector_geojson | vector_kml | raster_geotiff
    name: str
    url: str
    out_path: Path
    error: str = ""


def _safe_filename(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s[:220]


def _http_get_text(url: str, *, timeout: int, verify_tls: bool) -> str:
    r = requests.get(url, timeout=timeout, verify=verify_tls)
    r.raise_for_status()
    return r.text


def _stream_download(url: str, out_path: Path, *, timeout: int, verify_tls: bool) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".part")

    with requests.get(url, timeout=timeout, stream=True, verify=verify_tls) as r:
        r.raise_for_status()
        n = 0
        with tmp.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue
                f.write(chunk)
                n += len(chunk)

    tmp.replace(out_path)
    return n


def _download_with_retries(
    *,
    session: requests.Session,
    url: str,
    out_path: Path,
    timeout: int,
    verify_tls: bool,
    max_attempts: int,
    backoff_s: float,
) -> tuple[bool, int, str]:
    """Return (ok, bytes, error_message)."""

    last_err = ""
    for attempt in range(1, max_attempts + 1):
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = out_path.with_suffix(out_path.suffix + ".part")
            n = 0
            with session.get(url, timeout=timeout, stream=True, verify=verify_tls) as r:
                r.raise_for_status()
                # Defensive: avoid writing XML/HTML error bodies as .tif
                ct = (r.headers.get("content-type") or "").lower()
                if out_path.suffix.lower() == ".tif" and ("xml" in ct or "html" in ct):
                    body = r.text[:500].replace("\n", " ")
                    raise RuntimeError(f"Unexpected content-type for GeoTIFF: {ct} :: {body}")
                with tmp.open("wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 256):
                        if not chunk:
                            continue
                        f.write(chunk)
                        n += len(chunk)
            tmp.replace(out_path)
            return True, n, ""
        except (ChunkedEncodingError, ConnectionError, ReadTimeout) as e:
            last_err = f"{type(e).__name__}: {e}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"

        # cleanup partial file
        try:
            part = out_path.with_suffix(out_path.suffix + ".part")
            if part.exists():
                part.unlink()
        except Exception:
            pass

        if attempt < max_attempts:
            sleep_s = backoff_s * (2 ** (attempt - 1))
            time.sleep(min(60.0, sleep_s))

    return False, 0, last_err


def _parse_wfs_typenames(xml: str) -> list[str]:
    names = re.findall(r"<\s*Name\s*>([^<]+)<\s*/\s*Name\s*>", xml, flags=re.IGNORECASE)
    return [n.strip() for n in names if ":" in n]


def _parse_wcs_coverage_ids(xml: str) -> list[str]:
    ids = re.findall(
        r"<\s*(?:wcs:)?CoverageId\s*>([^<]+)<\s*/\s*(?:wcs:)?CoverageId\s*>",
        xml,
        flags=re.IGNORECASE,
    )
    return [i.strip() for i in ids if i.strip()]


def _build_items_for_patterns(
    *,
    typenames: list[str],
    coverage_ids: list[str],
    patterns: list[str],
    out_dir: Path,
    geoserver_base: str,
    include_rasters: bool,
) -> list[DownloadItem]:
    base = geoserver_base.rstrip("/")
    rx_list = [re.compile(p, flags=re.IGNORECASE) for p in patterns]

    def matches_any(s: str) -> bool:
        return any(rx.search(s) for rx in rx_list)

    # vectors
    matched_types = sorted({t for t in typenames if matches_any(t)})

    vectors_geojson_dir = out_dir / "vectors_geojson"
    vectors_kml_dir = out_dir / "vectors_kml"
    rasters_dir = out_dir / "rasters_geotiff"

    items: list[DownloadItem] = []

    for t in matched_types:
        safe = _safe_filename(t)
        geojson_url = (
            f"{base}/ows?service=WFS&version={DEFAULT_WFS_VERSION}&request=GetFeature"
            f"&typeName={t}&outputFormat=application/json"
        )
        kml_url = (
            f"{base}/ows?service=WFS&version={DEFAULT_WFS_VERSION}&request=GetFeature"
            f"&typeName={t}&outputFormat=application/vnd.google-earth.kml+xml"
        )
        items.append(
            DownloadItem("vector_geojson", t, geojson_url, vectors_geojson_dir / f"{safe}.geojson")
        )
        items.append(DownloadItem("vector_kml", t, kml_url, vectors_kml_dir / f"{safe}.kml"))

    # rasters
    if include_rasters:
        matched_cov = sorted({c for c in coverage_ids if matches_any(c)})
        for cid in matched_cov:
            safe = _safe_filename(cid)
            tif_url = (
                f"{base}/ows?service=WCS&version={DEFAULT_WCS_VERSION}&request=GetCoverage"
                f"&CoverageId={cid}&format=geotiff"
                f"&compression=LZW&tiling=true&tileheight=256&tilewidth=256"
            )
            items.append(DownloadItem("raster_geotiff", cid, tif_url, rasters_dir / f"{safe}.tif"))

    return items


def _write_manifest(pack_dir: Path, items: list[DownloadItem]) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    manifest = pack_dir / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "name", "url", "out_path", "exists", "bytes", "error"])
        for it in items:
            exists = it.out_path.exists()
            size = it.out_path.stat().st_size if exists else ""
            w.writerow(
                [
                    it.kind,
                    it.name,
                    it.url,
                    str(it.out_path.relative_to(WORKSPACE_ROOT)),
                    exists,
                    size,
                    it.error or "",
                ]
            )


def _write_readme(pack_dir: Path, patterns: list[str], include_rasters: bool, geoserver_base: str) -> None:
    txt = "\n".join(
        [
            f"# Core Stack Offline Pack — {pack_dir.name}",
            "",
            "This folder contains locally-downloaded Core Stack GeoServer layers matching patterns:",
            *[f"- `{p}`" for p in patterns],
            "",
            "## Contents",
            "- `vectors_geojson/` — vectors as GeoJSON (QGIS offline)",
            "- `vectors_kml/` — vectors as KML (Google Earth Pro offline)",
            "- `rasters_geotiff/` — rasters as GeoTIFF (QGIS offline)",
            "- `manifest.csv` — inventory",
            "",
            "## Notes",
            f"- Source GeoServer: `{geoserver_base}`",
            f"- Rasters included: `{include_rasters}`",
            "- GeoTIFFs will not display directly in Google Earth Pro.",
            "",
        ]
    )
    (pack_dir / "README.md").write_text(txt, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Core Stack GeoServer layers for offline use")
    parser.add_argument(
        "--geoserver-base",
        default=DEFAULT_GEOSERVER_BASE,
        help=f"GeoServer base URL (default: {DEFAULT_GEOSERVER_BASE})",
    )
    parser.add_argument(
        "--pack-name",
        default="dk_chikmagalur",
        help="Output pack folder name under outputs/corestack_offline_pack/",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        default=[],
        help="Regex pattern to match (can be passed multiple times).",
    )
    parser.add_argument(
        "--include-rasters",
        action="store_true",
        help="Also download WCS coverages as GeoTIFF (can be large).",
    )
    parser.add_argument(
        "--verify-tls",
        action="store_true",
        help="Verify TLS certificates (off by default; some 8443 cert chains may fail).",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.05,
        help="Sleep between downloads (seconds).",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Only discover and write manifest/README; do not download.",
    )
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Only attempt downloads where the output file is missing/empty.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=6,
        help="Retry attempts per item (network/server can reset big WCS downloads).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Per-request timeout in seconds (rasters can be slow).",
    )

    args = parser.parse_args()

    patterns = args.pattern or [r"dakshina_kannada_", r"chikmagalur_", r"chikkamagaluru_"]

    base = str(args.geoserver_base).rstrip("/")
    pack_dir = OUT_ROOT / str(args.pack_name)
    pack_dir.mkdir(parents=True, exist_ok=True)

    wfs_caps_url = f"{base}/ows?service=WFS&version={DEFAULT_WFS_VERSION}&request=GetCapabilities"
    wfs_xml = _http_get_text(wfs_caps_url, timeout=240, verify_tls=bool(args.verify_tls))
    typenames = _parse_wfs_typenames(wfs_xml)

    coverage_ids: list[str] = []
    if args.include_rasters:
        wcs_caps_url = f"{base}/ows?service=WCS&version={DEFAULT_WCS_VERSION}&request=GetCapabilities"
        wcs_xml = _http_get_text(wcs_caps_url, timeout=240, verify_tls=bool(args.verify_tls))
        coverage_ids = _parse_wcs_coverage_ids(wcs_xml)

    items = _build_items_for_patterns(
        typenames=typenames,
        coverage_ids=coverage_ids,
        patterns=patterns,
        out_dir=pack_dir,
        geoserver_base=base,
        include_rasters=bool(args.include_rasters),
    )

    _write_manifest(pack_dir, items)
    _write_readme(pack_dir, patterns, bool(args.include_rasters), base)

    if args.discover_only:
        print(f"Wrote: {pack_dir / 'manifest.csv'}")
        print(f"Wrote: {pack_dir / 'README.md'}")
        print(f"Discovered items: {len(items)}")
        return

    session = requests.Session()

    downloaded = 0
    skipped = 0
    failed = 0

    updated_items: list[DownloadItem] = []
    for it in items:
        exists_ok = it.out_path.exists() and it.out_path.stat().st_size > 0
        if exists_ok and args.only_missing:
            skipped += 1
            updated_items.append(it)
            continue

        if exists_ok:
            skipped += 1
            updated_items.append(it)
            continue

        ok, n, err = _download_with_retries(
            session=session,
            url=it.url,
            out_path=it.out_path,
            timeout=int(args.timeout),
            verify_tls=bool(args.verify_tls),
            max_attempts=int(args.max_attempts),
            backoff_s=2.0,
        )
        if ok:
            downloaded += 1
            updated_items.append(DownloadItem(it.kind, it.name, it.url, it.out_path, ""))
            print(f"Downloaded {it.kind}: {it.name} ({n/1024/1024:.2f} MB)")
        else:
            failed += 1
            updated_items.append(DownloadItem(it.kind, it.name, it.url, it.out_path, err))
            print(f"FAILED {it.kind}: {it.name} :: {err}")

        if args.sleep:
            time.sleep(float(args.sleep))

    _write_manifest(pack_dir, updated_items)

    print(f"Pack: {pack_dir}")
    print(f"Items: {len(items)} | downloaded: {downloaded} | skipped: {skipped} | failed: {failed}")


if __name__ == "__main__":
    main()
