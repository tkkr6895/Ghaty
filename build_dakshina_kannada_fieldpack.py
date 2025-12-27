"""Build a Dakshina Kannada (Karnataka) mobile-friendly "field pack".

Outputs:
- Clipped rasters (UTM Zone 43N)
- Mobile PNG maps (1080px wide)
- CSV tables with area statistics
- A concise Markdown README + manifest

This script is designed to run in the *base* Python environment and calls GDAL
binaries shipped with QGIS (no venv installs).
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd


WORKSPACE_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = WORKSPACE_ROOT / "outputs" / "dakshina_kannada_fieldpack"

DISTRICTS_SHP = WORKSPACE_ROOT / "district_boundaries" / "2011_Dist.shp"

CORESTACK_ACTIVE_JSON = (
    WORKSPACE_ROOT
    / "outputs"
    / "corestack_coverage"
    / "corestack_active_locations.json"
)

QGIS_GDAL_BIN = Path(r"C:\Program Files\QGIS 3.42.1\bin")
GDALINFO = QGIS_GDAL_BIN / "gdalinfo.exe"
GDALWARP = QGIS_GDAL_BIN / "gdalwarp.exe"
GDALDEM = QGIS_GDAL_BIN / "gdaldem.exe"
GDAL_TRANSLATE = QGIS_GDAL_BIN / "gdal_translate.exe"

TARGET_EPSG = "EPSG:32643"  # UTM zone 43N (covers Dakshina Kannada)
TARGET_TR_METERS = 30


LULC_CLASSES = {
    0: "Water",
    1: "Trees",
    2: "Grass",
    3: "Flooded vegetation",
    4: "Crops",
    5: "Shrub and scrub",
    6: "Built",
    7: "Bare",
    8: "Snow and ice",
}

CLASS_COLORS = {
    "Water": "#1976D2",
    "Trees": "#2E7D32",
    "Grass": "#689F38",
    "Flooded vegetation": "#00796B",
    "Crops": "#F57C00",
    "Shrub and scrub": "#795548",
    "Built": "#D32F2F",
    "Bare": "#757575",
    "Snow and ice": "#E0E0E0",
}


@dataclass(frozen=True)
class RasterSource:
    kind: str  # lulc_glc | built_glc | trees_glc | built_dw
    year: int
    path: Path


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + " ".join(cmd)
            + "\n\nSTDOUT:\n"
            + (proc.stdout or "")
            + "\n\nSTDERR:\n"
            + (proc.stderr or "")
        )


def _read_gdalinfo_json(path: Path, *, hist: bool = False) -> dict[str, Any]:
    cmd = [str(GDALINFO), "-json"]
    if hist:
        cmd.append("-hist")
    cmd.append(str(path))

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"gdalinfo failed for {path}:\n{proc.stderr or proc.stdout or ''}"
        )

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse gdalinfo JSON for {path}: {e}") from e


def ensure_dirs() -> dict[str, Path]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    paths = {
        "rasters": OUTPUT_ROOT / "rasters",
        "maps": OUTPUT_ROOT / "maps",
        "tables": OUTPUT_ROOT / "tables",
        "meta": OUTPUT_ROOT / "meta",
    }
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)
    return paths


def extract_dakshina_kannada_boundary(paths: dict[str, Path]) -> Path:
    gdf = gpd.read_file(DISTRICTS_SHP)

    # Field names observed in this workspace: ST_NM (state), DISTRICT (district)
    mask = (gdf["ST_NM"].str.lower() == "karnataka") & (
        gdf["DISTRICT"].str.lower() == "dakshina kannada"
    )
    dk = gdf.loc[mask].copy()
    if dk.empty:
        raise RuntimeError(
            "Could not find Dakshina Kannada in district boundaries. "
            "Expected ST_NM='Karnataka' and DISTRICT='Dakshina Kannada'."
        )

    dk = dk.to_crs("EPSG:4326")
    out = paths["meta"] / "dakshina_kannada_boundary.geojson"
    dk[["ST_NM", "DISTRICT", "geometry"]].to_file(out, driver="GeoJSON")
    return out


def discover_sources() -> list[RasterSource]:
    base = WORKSPACE_ROOT / "gdrive_exports" / "Wester Ghats Layers" / "GLC_Western_Ghats_Complete_Analysis"

    sources: list[RasterSource] = []
    for year in [1987, 1992, 1997, 2000, 2005, 2010]:
        sources.append(
            RasterSource(
                kind="lulc_glc",
                year=year,
                path=base / f"lulc_{year}_glc-fcs30d.tif",
            )
        )
        sources.append(
            RasterSource(
                kind="trees_glc",
                year=year,
                path=base / f"trees_{year}_glc-fcs30d.tif",
            )
        )
        sources.append(
            RasterSource(
                kind="built_glc",
                year=year,
                path=base / "built_glc" / f"built_{year}_glc-fcs30d.tif",
            )
        )

    built_dw = (
        WORKSPACE_ROOT
        / "gdrive_exports"
        / "Wester Ghats Layers"
        / "Western_Ghats_Built_Area"
    )
    for year in range(2018, 2026):
        sources.append(
            RasterSource(
                kind="built_dw",
                year=year,
                path=built_dw / f"built_area_{year}_january.tif",
            )
        )

    return sources


def write_color_files(paths: dict[str, Path]) -> dict[str, Path]:
    out: dict[str, Path] = {}

    # LULC (0..7 used in these exports; keep 8 in file for safety)
    lulc_txt = paths["meta"] / "lulc_colors.txt"
    lines = ["# value R G B A\n"]
    for code in sorted(LULC_CLASSES.keys()):
        label = LULC_CLASSES[code]
        if label not in CLASS_COLORS:
            continue
        r, g, b = _hex_to_rgb(CLASS_COLORS[label])
        lines.append(f"{code} {r} {g} {b} 255\n")
    # nodata (255) -> transparent
    lines.append("255 0 0 0 0\n")
    lulc_txt.write_text("".join(lines), encoding="utf-8")
    out["lulc"] = lulc_txt

    # Binary rasters
    built_txt = paths["meta"] / "built_binary_colors.txt"
    r, g, b = _hex_to_rgb(CLASS_COLORS["Built"])
    built_txt.write_text(
        "".join(
            [
                "# value R G B A\n",
                "0 0 0 0 0\n",
                f"1 {r} {g} {b} 255\n",
            ]
        ),
        encoding="utf-8",
    )
    out["built"] = built_txt

    trees_txt = paths["meta"] / "trees_binary_colors.txt"
    r, g, b = _hex_to_rgb(CLASS_COLORS["Trees"])
    trees_txt.write_text(
        "".join(
            [
                "# value R G B A\n",
                "0 0 0 0 0\n",
                f"1 {r} {g} {b} 255\n",
            ]
        ),
        encoding="utf-8",
    )
    out["trees"] = trees_txt

    return out


def clip_raster_to_district(
    source: RasterSource,
    boundary_geojson: Path,
    out_raster: Path,
) -> None:
    out_raster.parent.mkdir(parents=True, exist_ok=True)

    # Pick nodata so it can be excluded from histogram.
    if source.kind == "lulc_glc":
        dstnodata = "255"
    else:
        dstnodata = "0"

    cmd = [
        str(GDALWARP),
        "-overwrite",
        "-multi",
        "-wo",
        "NUM_THREADS=ALL_CPUS",
        "-cutline",
        str(boundary_geojson),
        "-crop_to_cutline",
        "-dstnodata",
        dstnodata,
        "-t_srs",
        TARGET_EPSG,
        "-tr",
        str(TARGET_TR_METERS),
        str(TARGET_TR_METERS),
        "-r",
        "near",
        str(source.path),
        str(out_raster),
    ]
    _run(cmd)


def render_mobile_png(
    source: RasterSource,
    clipped_raster: Path,
    color_file: Path,
    out_png: Path,
) -> None:
    tmp_colorized = out_png.with_suffix(".colorized.tif")

    # Use color-relief to RGBA (with alpha), then scale to a fixed mobile width.
    _run(
        [
            str(GDALDEM),
            "color-relief",
            "-alpha",
            str(clipped_raster),
            str(color_file),
            str(tmp_colorized),
        ]
    )

    _run(
        [
            str(GDAL_TRANSLATE),
            "-of",
            "PNG",
            "-outsize",
            "1080",
            "0",
            str(tmp_colorized),
            str(out_png),
        ]
    )

    try:
        tmp_colorized.unlink(missing_ok=True)
        tmp_aux = tmp_colorized.with_suffix(tmp_colorized.suffix + ".aux.xml")
        tmp_aux.unlink(missing_ok=True)
    except OSError:
        pass


def _pixel_area_km2_utm(clipped_raster: Path) -> float:
    info = _read_gdalinfo_json(clipped_raster, hist=False)
    gt = info.get("geoTransform")
    if not gt or len(gt) < 6:
        raise RuntimeError(f"Missing geotransform for {clipped_raster}")
    pixel_w_m = float(gt[1])
    pixel_h_m = abs(float(gt[5]))
    return (pixel_w_m * pixel_h_m) / 1_000_000.0


def value_histogram_counts(clipped_raster: Path) -> list[int]:
    info = _read_gdalinfo_json(clipped_raster, hist=True)
    bands = info.get("bands") or []
    if not bands:
        raise RuntimeError(f"No bands found in {clipped_raster}")

    hist = (bands[0] or {}).get("histogram")
    if not hist:
        raise RuntimeError(f"No histogram returned for {clipped_raster}")

    buckets = hist.get("buckets")
    if not isinstance(buckets, list):
        raise RuntimeError(
            f"Unexpected histogram buckets type for {clipped_raster}: {type(buckets)}"
        )

    # buckets is a 256-length list for byte rasters; index corresponds to value.
    return [int(x) for x in buckets]


def compute_tables(
    sources: list[RasterSource],
    clipped: dict[tuple[str, int], Path],
    paths: dict[str, Path],
) -> dict[str, Path]:
    out_files: dict[str, Path] = {}

    pixel_area_km2_cache: dict[Path, float] = {}

    def pixel_area_km2_for(path: Path) -> float:
        if path not in pixel_area_km2_cache:
            pixel_area_km2_cache[path] = _pixel_area_km2_utm(path)
        return pixel_area_km2_cache[path]

    # LULC composition (GLC)
    lulc_rows: list[dict[str, Any]] = []
    for s in sources:
        if s.kind != "lulc_glc":
            continue
        cr = clipped.get((s.kind, s.year))
        if not cr:
            continue

        buckets = value_histogram_counts(cr)
        pix_km2 = pixel_area_km2_for(cr)

        valid_counts = sum(buckets[v] for v in range(0, 255))
        if valid_counts <= 0:
            continue

        for code in range(0, 9):
            cnt = buckets[code] if code < len(buckets) else 0
            area = cnt * pix_km2
            pct = (cnt / valid_counts) * 100.0 if valid_counts else 0.0
            lulc_rows.append(
                {
                    "year": s.year,
                    "class_code": code,
                    "class_name": LULC_CLASSES.get(code, f"Class_{code}"),
                    "area_km2": area,
                    "percent": pct,
                }
            )

    if lulc_rows:
        df = pd.DataFrame(lulc_rows).sort_values(["year", "class_code"]) 
        out = paths["tables"] / "dakshina_kannada_lulc_glc_composition.csv"
        df.to_csv(out, index=False)
        out_files["lulc_glc_composition"] = out

    # Trees (GLC) binary
    trees_rows: list[dict[str, Any]] = []
    for s in sources:
        if s.kind != "trees_glc":
            continue
        cr = clipped.get((s.kind, s.year))
        if not cr:
            continue

        buckets = value_histogram_counts(cr)
        pix_km2 = pixel_area_km2_for(cr)

        cnt_tree = buckets[1] if len(buckets) > 1 else 0
        cnt_valid = sum(buckets[v] for v in range(0, 255))
        area_tree = cnt_tree * pix_km2
        pct_tree = (cnt_tree / cnt_valid) * 100.0 if cnt_valid else 0.0

        trees_rows.append(
            {
                "year": s.year,
                "tree_area_km2": area_tree,
                "tree_percent": pct_tree,
            }
        )

    if trees_rows:
        df = pd.DataFrame(trees_rows).sort_values(["year"])
        out = paths["tables"] / "dakshina_kannada_tree_cover_glc.csv"
        df.to_csv(out, index=False)
        out_files["trees_glc"] = out

    # Built (GLC) binary
    built_glc_rows: list[dict[str, Any]] = []
    for s in sources:
        if s.kind != "built_glc":
            continue
        cr = clipped.get((s.kind, s.year))
        if not cr:
            continue

        buckets = value_histogram_counts(cr)
        pix_km2 = pixel_area_km2_for(cr)

        cnt_built = buckets[1] if len(buckets) > 1 else 0
        area_built = cnt_built * pix_km2
        built_glc_rows.append({"year": s.year, "built_area_km2": area_built})

    if built_glc_rows:
        df = pd.DataFrame(built_glc_rows).sort_values(["year"])
        out = paths["tables"] / "dakshina_kannada_built_glc.csv"
        df.to_csv(out, index=False)
        out_files["built_glc"] = out

    # Built (Dynamic World / 2018-2025) binary
    built_dw_rows: list[dict[str, Any]] = []
    for s in sources:
        if s.kind != "built_dw":
            continue
        cr = clipped.get((s.kind, s.year))
        if not cr:
            continue

        buckets = value_histogram_counts(cr)
        pix_km2 = pixel_area_km2_for(cr)

        cnt_built = buckets[1] if len(buckets) > 1 else 0
        area_built = cnt_built * pix_km2
        built_dw_rows.append({"year": s.year, "built_area_km2": area_built})

    if built_dw_rows:
        df = pd.DataFrame(built_dw_rows).sort_values(["year"])
        out = paths["tables"] / "dakshina_kannada_built_dynamic_world.csv"
        df.to_csv(out, index=False)
        out_files["built_dynamic_world"] = out

    return out_files


def export_forest_typology(paths: dict[str, Path]) -> Path | None:
    src = (
        WORKSPACE_ROOT
        / "outputs"
        / "forest_typology"
        / "statistics"
        / "district_forest_typology_20251214_113455.csv"
    )
    if not src.exists():
        return None

    df = pd.read_csv(src)
    # Expect district column first, state second (based on observed row)
    district_col = df.columns[0]
    state_col = df.columns[1]

    dk = df[(df[district_col].str.lower() == "dakshina kannada") & (df[state_col].str.lower() == "karnataka")]
    if dk.empty:
        return None

    out = paths["tables"] / "dakshina_kannada_forest_typology.csv"
    dk.to_csv(out, index=False)
    return out


def export_corestack_blocks(paths: dict[str, Path]) -> Path | None:
    if not CORESTACK_ACTIVE_JSON.exists():
        return None

    payload = json.loads(CORESTACK_ACTIVE_JSON.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []

    # Supported shape (observed): list[ {label/state, district:[{label/district, blocks:[{label/block, ...}]}]} ]
    if isinstance(payload, list):
        for state in payload:
            state_label = (state or {}).get("label") or (state or {}).get("state")
            for dist in (state or {}).get("district", []) or []:
                dist_label = (dist or {}).get("label") or (dist or {}).get("district")
                if str(dist_label).strip().lower() != "dakshina kannada":
                    continue
                for block in (dist or {}).get("blocks", []) or []:
                    rows.append(
                        {
                            "state": state_label,
                            "district": dist_label,
                            "block": (block or {}).get("label") or (block or {}).get("block"),
                            "raw": json.dumps(block, ensure_ascii=False),
                        }
                    )

    if not rows:
        return None

    out = paths["tables"] / "dakshina_kannada_corestack_blocks.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    return out


def write_readme(
    paths: dict[str, Path],
    table_files: dict[str, Path],
    map_files: list[Path],
    manifest_path: Path,
) -> Path:
    readme = OUTPUT_ROOT / "README_DAKSHINA_KANNADA.md"

    lines: list[str] = []
    lines.append("# Dakshina Kannada — Field Validation Pack\n")
    lines.append("\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append("\n")
    lines.append("## Contents\n")
    lines.append("- `maps/`: mobile-friendly PNG maps (1080px wide)\n")
    lines.append("- `rasters/`: clipped GeoTIFF rasters (UTM Zone 43N)\n")
    lines.append("- `tables/`: CSV statistics extracted from clipped rasters + existing district tables\n")
    lines.append("- `manifest.json`: full file manifest\n")
    lines.append("\n")

    lines.append("## Notes\n")
    lines.append(
        "- LULC class codes follow the workspace mapping used in scripts like `create_comprehensive_outputs.py` (0=Water, 1=Trees, …, 7=Bare).\n"
    )
    lines.append(
        "- Areas are computed from UTM pixel sizes after reprojection to EPSG:32643, and exclude NoData pixels.\n"
    )
    lines.append("\n")

    if table_files:
        lines.append("## Tables\n")
        for k, p in table_files.items():
            lines.append(f"- `{p.relative_to(OUTPUT_ROOT).as_posix()}` ({k})\n")
        lines.append("\n")

    if map_files:
        lines.append("## Maps\n")
        for p in sorted(map_files):
            lines.append(f"- `{p.relative_to(OUTPUT_ROOT).as_posix()}`\n")
        lines.append("\n")

    lines.append("## Manifest\n")
    lines.append(f"- `{manifest_path.relative_to(OUTPUT_ROOT).as_posix()}`\n")

    readme.write_text("".join(lines), encoding="utf-8")
    return readme


def main() -> None:
    for exe in [GDALINFO, GDALWARP, GDALDEM, GDAL_TRANSLATE]:
        if not exe.exists():
            raise RuntimeError(
                f"Required GDAL binary not found: {exe}. "
                "Update QGIS_GDAL_BIN in this script if QGIS is installed elsewhere."
            )

    paths = ensure_dirs()

    boundary_geojson = extract_dakshina_kannada_boundary(paths)
    color_files = write_color_files(paths)

    sources = discover_sources()

    clipped: dict[tuple[str, int], Path] = {}
    map_files: list[Path] = []
    skipped: list[dict[str, Any]] = []

    for s in sources:
        if not s.path.exists():
            skipped.append({"kind": s.kind, "year": s.year, "path": str(s.path), "reason": "missing"})
            continue

        out_raster = paths["rasters"] / f"dakshina_kannada_{s.kind}_{s.year}.tif"
        out_map = paths["maps"] / f"dakshina_kannada_{s.kind}_{s.year}_mobile.png"

        try:
            clip_raster_to_district(s, boundary_geojson, out_raster)

            if s.kind == "lulc_glc":
                color = color_files["lulc"]
            elif s.kind in {"built_glc", "built_dw"}:
                color = color_files["built"]
            elif s.kind == "trees_glc":
                color = color_files["trees"]
            else:
                color = color_files["lulc"]

            render_mobile_png(s, out_raster, color, out_map)

            clipped[(s.kind, s.year)] = out_raster
            map_files.append(out_map)
        except Exception as e:
            skipped.append(
                {
                    "kind": s.kind,
                    "year": s.year,
                    "path": str(s.path),
                    "reason": str(e),
                }
            )

    table_files = compute_tables(sources, clipped, paths)

    forest_typology = export_forest_typology(paths)
    if forest_typology:
        table_files["forest_typology"] = forest_typology

    corestack_blocks = export_corestack_blocks(paths)
    if corestack_blocks:
        table_files["corestack_blocks"] = corestack_blocks

    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "boundary_geojson": str(boundary_geojson.relative_to(WORKSPACE_ROOT)),
        "target_epsg": TARGET_EPSG,
        "target_tr_m": TARGET_TR_METERS,
        "tables": {k: str(v.relative_to(WORKSPACE_ROOT)) for k, v in table_files.items()},
        "maps": [str(p.relative_to(WORKSPACE_ROOT)) for p in map_files],
        "rasters": [str(p.relative_to(WORKSPACE_ROOT)) for p in clipped.values()],
        "skipped": skipped,
    }

    manifest_path = OUTPUT_ROOT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    write_readme(paths, table_files, map_files, manifest_path)

    print(f"Done. Outputs: {OUTPUT_ROOT}")
    if skipped:
        print(f"Skipped sources: {len(skipped)} (see manifest.json)")


if __name__ == "__main__":
    main()
