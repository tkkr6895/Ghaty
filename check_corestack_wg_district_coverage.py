"""Compute Western Ghats districts and check Core Stack API coverage.

- Western Ghats districts are derived by intersecting district boundaries with
  the Western Ghats boundary shapefile.
- Coverage is derived from Core Stack API `/get_active_locations/`.

Usage (PowerShell):
  $env:CORE_STACK_API_KEY = '...'
  python check_corestack_wg_district_coverage.py

Outputs:
  outputs/corestack_coverage/western_ghats_districts.csv
  outputs/corestack_coverage/corestack_active_locations.json
  outputs/corestack_coverage/wg_district_coverage.csv
  outputs/corestack_coverage/wg_district_coverage.md
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import requests
from shapely import make_valid


WORKSPACE_ROOT = Path(__file__).resolve().parent

DISTRICTS_SHP = WORKSPACE_ROOT / "district_boundaries" / "2011_Dist.shp"
WESTERN_GHATS_SHP = WORKSPACE_ROOT / "data" / "western_ghats_boundary.shp"

OUTPUT_DIR = WORKSPACE_ROOT / "outputs" / "corestack_coverage"

DEFAULT_BASE_URL = "https://geoserver.core-stack.org/api/v1"
ACTIVE_LOCATIONS_PATH = "/get_active_locations/"


@dataclass(frozen=True)
class DistrictRecord:
    state: str
    district: str


def _normalize_for_corestack(name: str) -> str:
    value = str(name).strip().lower()
    value = value.replace("&", "and")
    value = re.sub(r"[\./'()]", "", value)
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[-]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value


def compute_western_ghats_districts() -> list[DistrictRecord]:
    if not DISTRICTS_SHP.exists():
        raise FileNotFoundError(f"Missing districts shapefile: {DISTRICTS_SHP}")
    if not WESTERN_GHATS_SHP.exists():
        raise FileNotFoundError(f"Missing Western Ghats shapefile: {WESTERN_GHATS_SHP}")

    districts = gpd.read_file(DISTRICTS_SHP)
    wg = gpd.read_file(WESTERN_GHATS_SHP).to_crs(districts.crs)

    # Repair invalid geometries in the WG boundary to avoid topology errors.
    wg["geometry"] = wg["geometry"].apply(make_valid)

    joined = gpd.sjoin(
        districts,
        wg[["geometry"]],
        how="inner",
        predicate="intersects",
    )

    # Expected columns in district boundaries.
    if "ST_NM" not in joined.columns or "DISTRICT" not in joined.columns:
        raise KeyError(
            "Expected ST_NM and DISTRICT fields in 2011_Dist.shp; "
            f"found columns: {list(joined.columns)}"
        )

    joined["ST_NM"] = joined["ST_NM"].astype(str).str.strip()
    joined["DISTRICT"] = joined["DISTRICT"].astype(str).str.strip()

    pairs = sorted(set(zip(joined["ST_NM"], joined["DISTRICT"])))
    return [DistrictRecord(state=st, district=dist) for st, dist in pairs]


def fetch_active_locations(base_url: str, api_key: str, timeout_s: int = 60) -> dict[str, Any]:
    url = base_url.rstrip("/") + ACTIVE_LOCATIONS_PATH
    headers = {"X-API-Key": api_key}
    response = requests.get(url, headers=headers, timeout=timeout_s)

    if response.status_code == 401:
        raise PermissionError(
            "Core Stack returned 401 Unauthorized. "
            "Check CORE_STACK_API_KEY and whether the endpoint expects this key."
        )

    response.raise_for_status()
    return response.json()


def _flatten_active_locations(payload: dict[str, Any]) -> set[tuple[str, str]]:
    covered: set[tuple[str, str]] = set()

    # The Swagger example shows a dict-of-dicts shape:
    # {"state_name": {"districts": {"district_name": {"tehsils": [...]}}}}
    if isinstance(payload, dict):
        for state_key, state_value in (payload or {}).items():
            districts = (state_value or {}).get("districts", {})
            if not isinstance(districts, dict):
                continue

            for district_key in districts.keys():
                covered.add(
                    (
                        _normalize_for_corestack(state_key),
                        _normalize_for_corestack(district_key),
                    )
                )

        return covered

    # The live endpoint currently returns a list of states:
    # [{"label": "State", "district": [{"label": "District", "blocks": [...]}]}]
    if isinstance(payload, list):
        for state_item in payload:
            if not isinstance(state_item, dict):
                continue

            state_name = state_item.get("label") or state_item.get("state")
            if not state_name:
                continue

            districts_list = state_item.get("district") or state_item.get("districts") or []
            if not isinstance(districts_list, list):
                continue

            for district_item in districts_list:
                if not isinstance(district_item, dict):
                    continue

                district_name = district_item.get("label") or district_item.get("district")
                if not district_name:
                    continue

                covered.add(
                    (
                        _normalize_for_corestack(state_name),
                        _normalize_for_corestack(district_name),
                    )
                )

    return covered


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    base_url = os.getenv("CORE_STACK_BASE_URL", DEFAULT_BASE_URL)
    api_key = os.getenv("CORE_STACK_API_KEY", "").strip()

    wg_districts = compute_western_ghats_districts()

    wg_df = pd.DataFrame(
        {
            "state": [d.state for d in wg_districts],
            "district": [d.district for d in wg_districts],
            "state_corestack": [_normalize_for_corestack(d.state) for d in wg_districts],
            "district_corestack": [_normalize_for_corestack(d.district) for d in wg_districts],
        }
    ).sort_values(["state", "district"], ignore_index=True)

    wg_df.to_csv(OUTPUT_DIR / "western_ghats_districts.csv", index=False)

    if not api_key:
        (OUTPUT_DIR / "wg_district_coverage.md").write_text(
            "# Core Stack Coverage Check (Western Ghats Districts)\n\n"
            "Computed Western Ghats districts, but did not query Core Stack because `CORE_STACK_API_KEY` is not set.\n\n"
            "## Next step\n\n"
            "Set the API key and rerun:\n\n"
            "```powershell\n"
            "$env:CORE_STACK_API_KEY = '...your key...'\n"
            "& 'C:/Users/trkumar/OneDrive - Deloitte (O365D)/Documents/Research/Western Ghats/venv_analysis/Scripts/python.exe' check_corestack_wg_district_coverage.py\n"
            "```\n"
        )

        wg_df.assign(corestack_covered=False).to_csv(
            OUTPUT_DIR / "wg_district_coverage.csv", index=False
        )
        print(f"Western Ghats districts extracted: {len(wg_df)}")
        print("CORE_STACK_API_KEY not set; wrote district list and placeholder coverage.")
        return 2

    active = fetch_active_locations(base_url=base_url, api_key=api_key)
    (OUTPUT_DIR / "corestack_active_locations.json").write_text(
        json.dumps(active, indent=2, sort_keys=True), encoding="utf-8"
    )

    covered_pairs = _flatten_active_locations(active)

    wg_df["corestack_covered"] = wg_df.apply(
        lambda row: (row["state_corestack"], row["district_corestack"]) in covered_pairs,
        axis=1,
    )

    wg_df.to_csv(OUTPUT_DIR / "wg_district_coverage.csv", index=False)

    total = int(len(wg_df))
    covered = int(wg_df["corestack_covered"].sum())

    covered_list = wg_df[wg_df["corestack_covered"]][["state", "district"]]
    uncovered_list = wg_df[~wg_df["corestack_covered"]][["state", "district"]]

    md_lines: list[str] = []
    md_lines.append("# Core Stack Coverage Check (Western Ghats Districts)")
    md_lines.append("")
    md_lines.append(f"- Core Stack base URL: `{base_url}`")
    md_lines.append(f"- Western Ghats districts found: **{total}**")
    md_lines.append(f"- Covered by Core Stack active locations: **{covered}**")
    md_lines.append(f"- Not covered: **{total - covered}**")
    md_lines.append("")

    md_lines.append("## Covered districts")
    md_lines.append("")
    if covered == 0:
        md_lines.append("(none)")
    else:
        for _, r in covered_list.sort_values(["state", "district"]).iterrows():
            md_lines.append(f"- {r['state']} — {r['district']}")

    md_lines.append("")
    md_lines.append("## Not covered districts")
    md_lines.append("")
    for _, r in uncovered_list.sort_values(["state", "district"]).iterrows():
        md_lines.append(f"- {r['state']} — {r['district']}")

    (OUTPUT_DIR / "wg_district_coverage.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Western Ghats districts extracted: {total}")
    print(f"Core Stack districts covered (active locations): {covered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
