"""Download Core Stack *Dakshina Kannada* GeoServer layers for offline field use.

Why this exists
- Core Stack API `/get_generated_layer_urls/` currently errors for Dakshina Kannada.
- For field validation you asked for *no dependency* on Core Stack APIs/GeoServer.

Approach
- Query GeoServer WFS GetCapabilities (public) and discover typeNames that include
  `dakshina_kannada_` (e.g., `...:dakshina_kannada_sulya`).
- Download vectors as:
  - GeoJSON (WFS outputFormat=application/json)
  - KML (WFS outputFormat=application/vnd.google-earth.kml+xml) for offline Google Earth Pro
- Optionally query GeoServer WCS GetCapabilities and download rasters as GeoTIFF.

Outputs
- outputs/corestack_dakshina_kannada_offline/
  - vectors_geojson/
  - vectors_kml/
  - rasters_geotiff/   (optional)
  - manifest.csv
  - README.md

Usage (PowerShell)
- Ensure you can reach GeoServer on port 8443: `Test-NetConnection geoserver.core-stack.org -Port 8443`
- python download_corestack_dakshina_kannada_offline.py

Notes
- This script only downloads *published layers* containing `dakshina_kannada_`.
- If your network blocks port 8443 at some point, run this once on a network/VPN
  where it works, then carry the outputs offline.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests


WORKSPACE_ROOT = Path(__file__).resolve().parent
OUT_DIR = WORKSPACE_ROOT / "outputs" / "corestack_dakshina_kannada_offline"
VECTORS_GEOJSON_DIR = OUT_DIR / "vectors_geojson"
VECTORS_KML_DIR = OUT_DIR / "vectors_kml"
RASTERS_DIR = OUT_DIR / "rasters_geotiff"
MANIFEST_CSV = OUT_DIR / "manifest.csv"
README_MD = OUT_DIR / "README.md"

DEFAULT_GEOSERVER_BASE = "https://geoserver.core-stack.org:8443/geoserver"
DEFAULT_WFS_VERSION = "1.0.0"
DEFAULT_WCS_VERSION = "2.0.1"


@dataclass(frozen=True)
class DownloadItem:
    kind: str  # vector_geojson | vector_kml | raster_geotiff
    name: str
    url: str
    out_path: Path


def _http_get_text(url: str, *, timeout: int = 120, verify_tls: bool = False) -> str:
    r = requests.get(url, timeout=timeout, verify=verify_tls)
    r.raise_for_status()
    return r.text


def _stream_download(url: str, out_path: Path, *, timeout: int = 600, verify_tls: bool = False) -> int:
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


def _parse_wfs_typenames(wfs_capabilities_xml: str) -> list[str]:
    # WFS capabilities are XML; a simple regex is OK here.
    # This yields many <Name> entries; keep those with a namespace prefix.
    names = re.findall(r"<\s*Name\s*>([^<]+)<\s*/\s*Name\s*>", wfs_capabilities_xml, flags=re.IGNORECASE)
    typenames = [n.strip() for n in names if ":" in n]
    return typenames


def _parse_wcs_coverage_ids(wcs_capabilities_xml: str) -> list[str]:
    ids = re.findall(r"<\s*wcs:CoverageId\s*>([^<]+)<\s*/\s*wcs:CoverageId\s*>", wcs_capabilities_xml, flags=re.IGNORECASE)
    return [i.strip() for i in ids if ":" in i]


def _safe_filename(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s[:200]


def build_items(
    *,
    geoserver_base: str,
    pattern: str,
    include_rasters: bool,
    sleep_s: float,
    verify_tls: bool,
) -> list[DownloadItem]:
    base = geoserver_base.rstrip("/")

    wfs_caps_url = f"{base}/ows?service=WFS&version={DEFAULT_WFS_VERSION}&request=GetCapabilities"
    wfs_xml = _http_get_text(wfs_caps_url, timeout=180, verify_tls=verify_tls)
    typenames = _parse_wfs_typenames(wfs_xml)

    rx = re.compile(pattern, flags=re.IGNORECASE)
    dk_types = sorted({t for t in typenames if rx.search(t)})

    items: list[DownloadItem] = []

    # vectors (GeoJSON + KML)
    for t in dk_types:
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
            DownloadItem(
                kind="vector_geojson",
                name=t,
                url=geojson_url,
                out_path=VECTORS_GEOJSON_DIR / f"{safe}.geojson",
            )
        )
        items.append(
            DownloadItem(
                kind="vector_kml",
                name=t,
                url=kml_url,
                out_path=VECTORS_KML_DIR / f"{safe}.kml",
            )
        )

        if sleep_s:
            time.sleep(sleep_s)

    # rasters (WCS GeoTIFF)
    if include_rasters:
        wcs_caps_url = f"{base}/ows?service=WCS&version={DEFAULT_WCS_VERSION}&request=GetCapabilities"
        wcs_xml = _http_get_text(wcs_caps_url, timeout=180, verify_tls=verify_tls)
        cov_ids = _parse_wcs_coverage_ids(wcs_xml)
        dk_cov = sorted({c for c in cov_ids if rx.search(c)})

        for cid in dk_cov:
            safe = _safe_filename(cid)
            tif_url = (
                f"{base}/ows?service=WCS&version={DEFAULT_WCS_VERSION}&request=GetCoverage"
                f"&CoverageId={cid}&format=geotiff"
            )
            items.append(
                DownloadItem(
                    kind="raster_geotiff",
                    name=cid,
                    url=tif_url,
                    out_path=RASTERS_DIR / f"{safe}.tif",
                )
            )
            if sleep_s:
                time.sleep(sleep_s)

    return items


def write_manifest(items: list[DownloadItem]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "name", "url", "out_path", "exists", "bytes"])  # header
        for it in items:
            exists = it.out_path.exists()
            size = it.out_path.stat().st_size if exists else ""
            w.writerow([it.kind, it.name, it.url, str(it.out_path.relative_to(WORKSPACE_ROOT)), exists, size])


def write_readme(pattern: str, include_rasters: bool, geoserver_base: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    README_MD.write_text(
        "\n".join(
            [
                "# Core Stack — Dakshina Kannada Offline Pack",
                "",
                "This folder contains locally-downloaded Core Stack *published GeoServer layers* matching:",
                f"- Pattern: `{pattern}`",
                "",
                "## Contents",
                "- `vectors_geojson/` — vector layers as GeoJSON (QGIS offline)",
                "- `vectors_kml/` — vector layers as KML (Google Earth Pro offline)",
                "- `rasters_geotiff/` — raster layers as GeoTIFF (optional)",
                "- `manifest.csv` — inventory of downloaded items",
                "",
                "## Notes",
                f"- Source GeoServer base: `{geoserver_base}`",
                "- This pack is independent of Core Stack APIs during field work.",
                "- If you need rasters viewable in Google Earth Pro, we can add an optional step to generate KML super-overlays from the GeoTIFFs.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Dakshina Kannada Core Stack GeoServer layers for offline use")
    parser.add_argument(
        "--geoserver-base",
        default=DEFAULT_GEOSERVER_BASE,
        help=f"GeoServer base URL (default: {DEFAULT_GEOSERVER_BASE})",
    )
    parser.add_argument(
        "--pattern",
        default=r"dakshina_kannada_",
        help="Regex to match layer names (typeName or CoverageId). Default matches Dakshina Kannada layers.",
    )
    parser.add_argument(
        "--include-rasters",
        action="store_true",
        help="Also download WCS coverages as GeoTIFF (can be large).",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.05,
        help="Sleep between requests (seconds).",
    )
    parser.add_argument(
        "--verify-tls",
        action="store_true",
        help="Verify TLS certs (off by default, because 8443 cert validation may fail on some networks).",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=0,
        help="If >0, only download first N items (for quick tests).",
    )

    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    VECTORS_GEOJSON_DIR.mkdir(parents=True, exist_ok=True)
    VECTORS_KML_DIR.mkdir(parents=True, exist_ok=True)
    if args.include_rasters:
        RASTERS_DIR.mkdir(parents=True, exist_ok=True)

    items = build_items(
        geoserver_base=args.geoserver_base,
        pattern=args.pattern,
        include_rasters=bool(args.include_rasters),
        sleep_s=float(args.sleep),
        verify_tls=bool(args.verify_tls),
    )

    if args.max_items and args.max_items > 0:
        items = items[: args.max_items]

    downloaded = 0
    skipped = 0

    for it in items:
        if it.out_path.exists() and it.out_path.stat().st_size > 0:
            skipped += 1
            continue

        try:
            n = _stream_download(it.url, it.out_path, timeout=900, verify_tls=bool(args.verify_tls))
            downloaded += 1
            print(f"Downloaded {it.kind}: {it.name} -> {it.out_path.name} ({n/1024/1024:.2f} MB)")
        except Exception as e:
            print(f"FAILED {it.kind}: {it.name} :: {e}")

    write_manifest(items)
    write_readme(args.pattern, bool(args.include_rasters), args.geoserver_base)

    print(f"Wrote: {MANIFEST_CSV}")
    print(f"Wrote: {README_MD}")
    print(f"Items: {len(items)} | downloaded: {downloaded} | skipped: {skipped}")


if __name__ == "__main__":
    main()
