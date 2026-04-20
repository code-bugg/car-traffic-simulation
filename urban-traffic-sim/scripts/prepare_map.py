"""
prepare_map.py
==============
Downloads the Chișinău OSM road network and converts it to SUMO format.

Usage:
    python scripts/prepare_map.py
    python scripts/prepare_map.py --config config/simulation.yaml
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

import requests
import yaml

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/map"


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def download_osm(bbox: dict, out_path: Path) -> None:
    """Download raw OSM data for the given bounding box."""
    if out_path.exists():
        logger.info("OSM file already exists, skipping download: %s", out_path)
        return

    params = {
        "bbox": f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}"
    }
    headers = {"User-Agent": "urban-traffic-sim/1.0 (educational project)"}
    logger.info("Downloading OSM data for bbox %s ...", params["bbox"])
    response = requests.get(OVERPASS_URL, params=params, headers=headers, timeout=180)
    response.raise_for_status()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(response.content)
    logger.info("Saved OSM data → %s  (%.1f MB)",
                out_path, out_path.stat().st_size / 1e6)


def convert_to_sumo(osm_path: Path, net_path: Path) -> None:
    """Run netconvert to produce a SUMO .net.xml from the OSM file."""
    if net_path.exists():
        logger.info("Network file already exists, skipping conversion: %s", net_path)
        return

    cmd = [
        "netconvert",
        "--osm-files",          str(osm_path),
        "--output-file",        str(net_path),
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess-signals",
        "--tls.discard-simple",
        "--tls.join",
        "--keep-edges.by-vclass", "passenger,bus,truck",
        "--remove-edges.isolated",
        "--no-turnarounds",
        "--keep-edges.components", "1", # <--- FIXUL STRUCTURAL AICI
    ]
    logger.info("Running netconvert ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("netconvert failed:\n%s", result.stderr)
        sys.exit(1)
    logger.info("Network saved → %s", net_path)


def generate_routes(net_path: Path, rou_path: Path, cfg: dict, force: bool = False) -> None:
    """
    Generate random routes using randomTrips.py (ships with SUMO).
    Falls back to a minimal hand-written route file if SUMO_HOME is unset.
    Pass force=True to regenerate even when the file already exists.
    """
    if rou_path.exists() and not force:
        logger.info("Route file already exists, skipping: %s", rou_path)
        return
    if rou_path.exists() and force:
        logger.info("Removing existing route file for regeneration: %s", rou_path)
        rou_path.unlink()

    sumo_home = os.environ.get("SUMO_HOME")
    random_trips = None
    if sumo_home:
        candidates = [
            Path(sumo_home) / "tools" / "randomTrips.py",
            Path(sumo_home) / "tools" / "trip" / "randomTrips.py",
        ]
        for c in candidates:
            if c.exists():
                random_trips = c
                break

    if random_trips:
        sim = cfg["simulation"]
        cmd = [
            sys.executable, str(random_trips),
            "--net-file",   str(net_path),
            "--output-trip-file", str(rou_path).replace(".rou.xml", ".trip.xml"),
            "--route-file", str(rou_path),
            "--end",        str(sim["total_steps"]),
            "--period",     str(cfg["traffic"]["spawn_interval"]),
            "--seed",       str(sim["seed"]),
            "--vehicle-class", "passenger",
            "--validate",
        ]
        logger.info("Generating random routes ...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning("randomTrips.py failed: %s", result.stderr)
        else:
            logger.info("Routes saved → %s", rou_path)
            return

    # Fallback: minimal stub so the project at least parses
    logger.warning("Writing minimal stub route file (set SUMO_HOME for real routes).")
    rou_path.write_text(
        '<routes>\n'
        '  <!-- Add <vehicle> or <flow> elements here -->\n'
        '</routes>\n'
    )


def generate_poly(net_path: Path, poly_path: Path, osm_path: Path) -> None:
    """Generate a polygon/POI file for buildings and land-use."""
    if poly_path.exists():
        return
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        poly_path.write_text("<additional/>\n")
        return
    typemap = Path(sumo_home) / "data" / "typemap" / "osmPolyconvert.typ.xml"
    if not typemap.exists():
        poly_path.write_text("<additional/>\n")
        return
    cmd = [
        "polyconvert",
        "--net-file",   str(net_path),
        "--osm-files",  str(osm_path),
        "--type-file",  str(typemap),
        "--output-file", str(poly_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning("polyconvert failed, writing empty poly file.")
        poly_path.write_text("<additional/>\n")
    else:
        logger.info("Polygons saved → %s", poly_path)


def main():
    parser = argparse.ArgumentParser(description="Prepare Chișinău SUMO map files.")
    parser.add_argument("--config", default="config/simulation.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    bbox = cfg["city"]["bbox"]
    maps = Path("maps")
    maps.mkdir(exist_ok=True)

    osm_path  = maps / "chisinau.osm"
    net_path  = maps / "chisinau.net.xml"
    rou_path  = maps / "chisinau.rou.xml"
    poly_path = maps / "chisinau.poly.xml"

    download_osm(bbox, osm_path)
    convert_to_sumo(osm_path, net_path)
    generate_routes(net_path, rou_path, cfg)
    generate_poly(net_path, poly_path, osm_path)

    logger.info("Map preparation complete. You can now run: python main.py")


if __name__ == "__main__":
    main()
