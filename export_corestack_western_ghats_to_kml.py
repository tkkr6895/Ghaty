"""Export Core Stack data for Western Ghats districts as a single KML.

Goal
- Make it easy to visualize "what Core Stack has" for Western Ghats districts in
  Google Earth / QGIS.

What this script does
1) Reads WG district list from outputs/corestack_coverage/western_ghats_districts.csv
2) Calls Core Stack /get_active_locations/ to discover which WG districts are active
3) For each active WG district and each active "block" (used as tehsil), calls
   /get_generated_layer_urls/ and collects the returned layers.
4) Writes a KML with a folder structure State -> District -> Tehsil/Block -> Layers.
   Each layer is written as a NetworkLink pointing to the GeoServer WFS URL but
   with outputFormat set to KML.
5) Optionally adds placemarks for user-provided GPS points and reverse-admin lookup
   via /get_admin_details_by_latlon/.

Auth
- Provide API key via env var CORESTACK_API_KEY
  PowerShell:  $env:CORESTACK_API_KEY = "<key>"

Usage
- python export_corestack_western_ghats_to_kml.py

Outputs
- outputs/corestack_wg_kml/corestack_western_ghats_layers.kml
- outputs/corestack_wg_kml/corestack_western_ghats_layers.csv
- outputs/corestack_wg_kml/admin_lookup_points.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import requests


WORKSPACE_ROOT = Path(__file__).resolve().parent
WG_DISTRICTS_CSV = WORKSPACE_ROOT / "outputs" / "corestack_coverage" / "western_ghats_districts.csv"
OUT_DIR = WORKSPACE_ROOT / "outputs" / "corestack_wg_kml"
OUT_KML = OUT_DIR / "corestack_western_ghats_layers.kml"
OUT_CSV = OUT_DIR / "corestack_western_ghats_layers.csv"
OUT_POINTS_CSV = OUT_DIR / "admin_lookup_points.csv"

CORESTACK_BASE_URL = os.environ.get("CORESTACK_BASE_URL", "https://api-doc.core-stack.org/api/v1")
API_KEY = os.environ.get("CORESTACK_API_KEY") or os.environ.get("CORE_STACK_API_KEY")

DEFAULT_USER_POINTS = [
    (12.98, 75.57, "Point 12.98, 75.57"),
    (13.10, 75.20, "Point 13.1, 75.2"),
]


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9_]+", "", s)
    return s


def _kml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _http_get(path: str, params: dict[str, Any] | None = None) -> Any:
    if not API_KEY:
        raise RuntimeError(
            "Missing API key env var. Set either CORESTACK_API_KEY or CORE_STACK_API_KEY and re-run."
        )

    url = CORESTACK_BASE_URL.rstrip("/") + path
    headers = {"X-API-Key": API_KEY}

    resp = requests.get(url, headers=headers, params=params, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(
            f"GET {url} failed: {resp.status_code} {resp.text[:500]}"
        )
    return resp.json()


def _flatten_active_locations(payload: Any) -> list[dict[str, str]]:
    """Return rows with (state, district, tehsil).

    Supports both:
    - Swagger example (dict keyed by state -> districts -> tehsils)
    - Observed live shape (list of states; each has district[]; each has blocks[])
    """

    rows: list[dict[str, str]] = []

    if isinstance(payload, dict):
        for state_name, state_obj in payload.items():
            districts = (state_obj or {}).get("districts") or {}
            for district_name, district_obj in districts.items():
                tehsils = (district_obj or {}).get("tehsils") or []
                if not tehsils:
                    rows.append({"state": str(state_name), "district": str(district_name), "tehsil": ""})
                else:
                    for t in tehsils:
                        rows.append({"state": str(state_name), "district": str(district_name), "tehsil": str(t)})
        return rows

    if isinstance(payload, list):
        for st in payload:
            state_label = (st or {}).get("label") or (st or {}).get("state") or ""
            for d in (st or {}).get("district", []) or []:
                district_label = (d or {}).get("label") or (d or {}).get("district") or ""
                blocks = (d or {}).get("blocks") or []
                if not blocks:
                    rows.append({"state": str(state_label), "district": str(district_label), "tehsil": ""})
                else:
                    for b in blocks:
                        tehsil_label = (b or {}).get("label") or (b or {}).get("block") or ""
                        rows.append(
                            {
                                "state": str(state_label),
                                "district": str(district_label),
                                "tehsil": str(tehsil_label),
                            }
                        )
        return rows

    raise RuntimeError(f"Unsupported active locations payload type: {type(payload)}")


def _wfs_url_to_kml(wfs_url: str) -> str:
    # GeoServer WFS commonly supports outputFormat=application/vnd.google-earth.kml+xml
    # If outputFormat is present, replace it; else append.
    if "outputFormat=" in wfs_url:
        return re.sub(
            r"outputFormat=[^&]+",
            "outputFormat=application/vnd.google-earth.kml+xml",
            wfs_url,
            flags=re.IGNORECASE,
        )
    sep = "&" if "?" in wfs_url else "?"
    return wfs_url + f"{sep}outputFormat=application/vnd.google-earth.kml+xml"


def _is_wfs_url(url: str) -> bool:
    u = url.lower()
    return "service=wfs" in u and "request=getfeature" in u


def _layer_url_to_kml_href(layer_url: str) -> str:
    if not layer_url:
        return ""
    if not _is_wfs_url(layer_url):
        return ""
    return _wfs_url_to_kml(layer_url)


def _read_user_points(points_csv: str | None) -> list[tuple[float, float, str]]:
    if not points_csv:
        return DEFAULT_USER_POINTS

    p = Path(points_csv)
    if not p.exists():
        raise RuntimeError(f"Points CSV not found: {p}")

    df = pd.read_csv(p)
    if not {"lat", "lon"}.issubset(set(df.columns)):
        raise RuntimeError(
            f"Points CSV must have columns lat, lon (optional: name). Got: {list(df.columns)}"
        )

    out: list[tuple[float, float, str]] = []
    for _, row in df.iterrows():
        lat = float(row["lat"])
        lon = float(row["lon"])
        name = str(row.get("name") or f"Point {lat}, {lon}")
        out.append((lat, lon, name))
    return out


def _local_admin_from_2011_districts(lat: float, lon: float) -> dict[str, str]:
    """Best-effort local district lookup (2011 Census districts).

    Returns empty dict if geopandas is unavailable or point is outside polygons.
    """

    try:
        import geopandas as gpd
        from shapely.geometry import Point
    except Exception:
        return {}

    shp = WORKSPACE_ROOT / "district_boundaries" / "2011_Dist.shp"
    if not shp.exists():
        return {}

    try:
        gdf = gpd.read_file(shp)
        if gdf.crs is None or str(gdf.crs).upper() != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
        p = Point(lon, lat)
        hit = gdf[gdf.contains(p)]
        if len(hit) == 0:
            hit = gdf[gdf.geometry.buffer(0).contains(p)]
        if len(hit) == 0:
            return {}
        row = hit.iloc[0]
        out: dict[str, str] = {}
        if "ST_NM" in hit.columns:
            out["local_state"] = str(row["ST_NM"])
        if "DISTRICT" in hit.columns:
            out["local_district"] = str(row["DISTRICT"])
        return out
    except Exception:
        return {}


def read_wg_district_set() -> set[tuple[str, str]]:
    if not WG_DISTRICTS_CSV.exists():
        raise RuntimeError(f"Missing {WG_DISTRICTS_CSV}")

    df = pd.read_csv(WG_DISTRICTS_CSV)
    # columns in this workspace: state, district, state_corestack, district_corestack
    out: set[tuple[str, str]] = set()
    for _, row in df.iterrows():
        out.add((str(row["state"]).strip().lower(), str(row["district"]).strip().lower()))
    return out


def write_kml(layer_rows: list[dict[str, Any]], point_rows: list[dict[str, Any]]) -> None:
    # Build a nested structure for easier KML emission
    tree: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = {}
    for r in layer_rows:
        tree.setdefault(r["state"], {}).setdefault(r["district"], {}).setdefault(r["tehsil"], []).append(r)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    kml_lines: list[str] = []
    kml_lines.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml_lines.append('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml_lines.append("<Document>\n")
    kml_lines.append(f"  <name>{_kml_escape('Core Stack — Western Ghats Layers')}</name>\n")
    kml_lines.append(
        "  <description>"
        + _kml_escape(
            "Notes:\n"
            "- This KML uses NetworkLinks that point to GeoServer URLs returned by Core Stack. Many of those URLs use geoserver.core-stack.org:8443. If your network blocks outbound port 8443 (common on corporate networks), Google Earth will not be able to fetch and display those layers.\n"
            "- This KML only creates live links for WFS vector layers (service=WFS). Raster/WCS layers cannot be streamed into Google Earth as KML via outputFormat and are therefore not linked as live layers here. Use the CSV inventory for QGIS/download workflows.\n"
            "- Any '(ERROR fetching layers)' entry means the Core Stack API /get_generated_layer_urls failed for that (state,district,tehsil) combination (e.g., server-side 'DistrictSOI matching query does not exist.')."
        )
        + "</description>\n"
    )

    # User points folder
    if point_rows:
        kml_lines.append("  <Folder>\n")
        kml_lines.append("    <name>User Points (Admin Lookup)</name>\n")
        for pr in point_rows:
            nm = pr.get("name") or f"{pr['lat']}, {pr['lon']}"
            desc = "\n".join(
                [
                    f"Latitude: {pr['lat']}",
                    f"Longitude: {pr['lon']}",
                    f"State: {pr.get('state','')}",
                    f"District: {pr.get('district','')}",
                    f"Tehsil: {pr.get('tehsil','')}",
                ]
            )
            kml_lines.append("    <Placemark>\n")
            kml_lines.append(f"      <name>{_kml_escape(nm)}</name>\n")
            kml_lines.append(f"      <description>{_kml_escape(desc)}</description>\n")
            kml_lines.append("      <Point>\n")
            kml_lines.append(f"        <coordinates>{pr['lon']},{pr['lat']},0</coordinates>\n")
            kml_lines.append("      </Point>\n")
            kml_lines.append("    </Placemark>\n")
        kml_lines.append("  </Folder>\n")

    # Main data folder
    kml_lines.append("  <Folder>\n")
    kml_lines.append("    <name>Western Ghats (Core Stack Active)</name>\n")

    for state in sorted(tree.keys()):
        kml_lines.append("    <Folder>\n")
        kml_lines.append(f"      <name>{_kml_escape(state)}</name>\n")

        for district in sorted(tree[state].keys()):
            kml_lines.append("      <Folder>\n")
            kml_lines.append(f"        <name>{_kml_escape(district)}</name>\n")

            for tehsil in sorted(tree[state][district].keys()):
                tehsil_name = tehsil if tehsil else "(no tehsil)"
                kml_lines.append("        <Folder>\n")
                kml_lines.append(f"          <name>{_kml_escape(tehsil_name)}</name>\n")

                layers = tree[state][district][tehsil]
                for layer in layers:
                    kml_url = layer.get("layer_kml_url") or ""
                    layer_name = layer.get("layer_name") or "(layer)"
                    layer_type = layer.get("layer_type") or ""

                    if kml_url:
                        kml_lines.append("          <NetworkLink>\n")
                        kml_lines.append(f"            <name>{_kml_escape(layer_name)}</name>\n")
                        kml_lines.append(
                            f"            <description>{_kml_escape(layer_type)}</description>\n"
                        )
                        kml_lines.append("            <Link>\n")
                        kml_lines.append(f"              <href>{_kml_escape(kml_url)}</href>\n")
                        kml_lines.append("            </Link>\n")
                        kml_lines.append("          </NetworkLink>\n")
                    else:
                        # Still emit a placemark listing the URL (if any)
                        desc = layer.get("layer_url") or ""
                        kml_lines.append("          <Placemark>\n")
                        kml_lines.append(f"            <name>{_kml_escape(layer_name)}</name>\n")
                        kml_lines.append(f"            <description>{_kml_escape(desc)}</description>\n")
                        kml_lines.append("          </Placemark>\n")

                kml_lines.append("        </Folder>\n")

            kml_lines.append("      </Folder>\n")

        kml_lines.append("    </Folder>\n")

    kml_lines.append("  </Folder>\n")
    kml_lines.append("</Document>\n")
    kml_lines.append("</kml>\n")

    OUT_KML.write_text("".join(kml_lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export Core Stack data for Western Ghats districts as a single KML."
    )
    parser.add_argument(
        "--points-csv",
        default=os.environ.get("CORESTACK_USER_POINTS_CSV", ""),
        help="Optional CSV with columns lat, lon (optional: name). Can also set CORESTACK_USER_POINTS_CSV.",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    wg_set = read_wg_district_set()

    # 1) Active locations
    active_payload = _http_get("/get_active_locations/")
    active_rows = _flatten_active_locations(active_payload)

    # 2) Filter to WG districts
    wg_active = [
        r
        for r in active_rows
        if (r["state"].strip().lower(), r["district"].strip().lower()) in wg_set
    ]

    # 3) For each WG active (state,district,tehsil), fetch layers
    layer_rows: list[dict[str, Any]] = []

    # de-dup (some payloads can repeat)
    seen: set[tuple[str, str, str]] = set()

    for r in wg_active:
        state = r["state"].strip()
        district = r["district"].strip()
        tehsil = r["tehsil"].strip()

        key = (state.lower(), district.lower(), tehsil.lower())
        if key in seen:
            continue
        seen.add(key)

        if not tehsil:
            # no tehsil/block available; still keep a row
            layer_rows.append(
                {
                    "state": state,
                    "district": district,
                    "tehsil": tehsil,
                    "layer_name": "(no tehsil in active locations)",
                    "layer_type": "",
                    "layer_url": "",
                    "layer_kml_url": "",
                    "layer_version": "",
                    "style_url": "",
                    "gee_asset_path": "",
                }
            )
            continue

        try:
            layers = _http_get(
                "/get_generated_layer_urls/",
                params={"state": state, "district": district, "tehsil": tehsil},
            )
        except Exception as e:
            layer_rows.append(
                {
                    "state": state,
                    "district": district,
                    "tehsil": tehsil,
                    "layer_name": "(ERROR fetching layers)",
                    "layer_type": "",
                    "layer_url": "",
                    "layer_kml_url": "",
                    "layer_version": "",
                    "style_url": "",
                    "gee_asset_path": "",
                    "error": str(e),
                }
            )
            continue

        if not isinstance(layers, list) or not layers:
            layer_rows.append(
                {
                    "state": state,
                    "district": district,
                    "tehsil": tehsil,
                    "layer_name": "(no layers returned)",
                    "layer_type": "",
                    "layer_url": "",
                    "layer_kml_url": "",
                    "layer_version": "",
                    "style_url": "",
                    "gee_asset_path": "",
                }
            )
            continue

        for layer in layers:
            layer_url = str((layer or {}).get("layer_url") or "")
            layer_rows.append(
                {
                    "state": state,
                    "district": district,
                    "tehsil": tehsil,
                    "layer_name": str((layer or {}).get("layer_name") or ""),
                    "layer_type": str((layer or {}).get("layer_type") or ""),
                    "layer_url": layer_url,
                        "layer_kml_url": _layer_url_to_kml_href(layer_url),
                    "layer_version": str((layer or {}).get("layer_version") or ""),
                    "style_url": str((layer or {}).get("style_url") or ""),
                    "gee_asset_path": str((layer or {}).get("gee_asset_path") or ""),
                }
            )

        # be polite to the API
        time.sleep(0.15)

    # 4) Admin lookup for user points
    point_rows: list[dict[str, Any]] = []
    user_points = _read_user_points(str(args.points_csv).strip() or None)
    for (lat, lon, name) in user_points:
        try:
            admin = _http_get(
                "/get_admin_details_by_latlon/",
                params={"latitude": lat, "longitude": lon},
            )
            local_admin = _local_admin_from_2011_districts(lat, lon)
            point_rows.append(
                {
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "state": (admin or {}).get("State", ""),
                    "district": (admin or {}).get("District", ""),
                    "tehsil": (admin or {}).get("Tehsil", ""),
                    **local_admin,
                }
            )
        except Exception as e:
            local_admin = _local_admin_from_2011_districts(lat, lon)
            point_rows.append(
                {
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "state": "",
                    "district": "",
                    "tehsil": "",
                    "error": str(e),
                    **local_admin,
                }
            )

    # 5) Write CSVs
    pd.DataFrame(layer_rows).to_csv(OUT_CSV, index=False)
    pd.DataFrame(point_rows).to_csv(OUT_POINTS_CSV, index=False)

    # 6) Write KML
    write_kml(layer_rows, point_rows)

    print(f"Wrote: {OUT_KML}")
    print(f"Wrote: {OUT_CSV}")
    print(f"Wrote: {OUT_POINTS_CSV}")
    print(f"Active WG locations (state/district/tehsil rows): {len(wg_active)}")


if __name__ == "__main__":
    main()
