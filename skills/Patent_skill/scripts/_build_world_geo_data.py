#!/usr/bin/env python3
"""One-time build step: fetch Natural Earth 110m country/land topojson from
unpkg.com/world-atlas@2 (public-domain Natural Earth data, ISC-licensed
topojson conversion) and bake it into scripts/_world_geo_data.py as plain SVG
path strings, pre-projected onto the equirectangular plot area used by
build_landscape_v2.py's jurisdiction map panel.

Run this only when the highlighted jurisdiction list changes (currently CN,
US, JP, and an EP proxy list of EPO contracting states matched by country
name - see NAME_TARGETS below). Needs network access to unpkg.com; the
generated _world_geo_data.py has no further runtime dependency (stdlib json
only, consumed by build_landscape_v2.py at report-build time - the browser
never re-fetches anything for this panel).

Usage: python scripts/_build_world_geo_data.py
"""

import json
import urllib.request
from pathlib import Path

COUNTRIES_URL = "https://unpkg.com/world-atlas@2/countries-110m.json"
LAND_URL = "https://unpkg.com/world-atlas@2/land-110m.json"

PLOT_W, PLOT_H = 880.0, 400.0  # must match Pw/Ph in build_landscape_v2.py's renderGeoMap

# EP is a schematic proxy (EPO contracting states matched by country name at
# 110m resolution, not a legally authoritative membership map); a few
# microstates (Monaco, San Marino, Liechtenstein, Malta) are omitted because
# they are not resolvable as separate polygons at this resolution.
LABEL_LONLAT = {
    "CN": (105, 35),
    "US": (-98, 39),
    "JP": (138, 36),
    "EP": (10, 50),
    "AU": (134, -25),
    "CA": (-96, 58),
    "MX": (-102, 23),
    "NZ": (172, -41),
}

NAME_TARGETS = {
    "CN": ["China"],
    "US": ["United States of America"],
    "JP": ["Japan"],
    "AU": ["Australia"],
    "CA": ["Canada"],
    "MX": ["Mexico"],
    "NZ": ["New Zealand"],
    "EP": [
        "Germany", "France", "United Kingdom", "Italy", "Spain", "Netherlands",
        "Belgium", "Switzerland", "Austria", "Sweden", "Poland", "Denmark",
        "Finland", "Norway", "Ireland", "Portugal", "Greece", "Czechia",
        "Hungary", "Romania", "Bulgaria", "Croatia", "Slovakia", "Slovenia",
        "Estonia", "Latvia", "Lithuania", "Luxembourg", "Iceland", "Cyprus",
        "Macedonia", "Albania", "Turkey",
    ],
}


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def decode_arc(deltas, transform):
    sx, sy = transform["scale"]
    tx, ty = transform["translate"]
    x = y = 0
    out = []
    for dx, dy in deltas:
        x += dx
        y += dy
        out.append((x * sx + tx, y * sy + ty))
    return out


def arc_points(arcs, index, transform):
    if index >= 0:
        return decode_arc(arcs[index], transform)
    pts = decode_arc(arcs[~index], transform)
    return list(reversed(pts))


def ring_points(arcs, ring_arc_indices, transform):
    pts = []
    for idx in ring_arc_indices:
        seg = arc_points(arcs, idx, transform)
        if pts and seg and pts[-1] == seg[0]:
            seg = seg[1:]
        pts.extend(seg)
    return pts


def geometry_rings(geom, arcs, transform):
    if geom["type"] == "Polygon":
        return [ring_points(arcs, ring, transform) for ring in geom["arcs"]]
    if geom["type"] == "MultiPolygon":
        rings = []
        for polygon in geom["arcs"]:
            for ring in polygon:
                rings.append(ring_points(arcs, ring, transform))
        return rings
    return []


def project(lon, lat):
    x = (lon + 180.0) / 360.0 * PLOT_W
    y = (90.0 - lat) / 180.0 * PLOT_H
    return x, y


def rings_to_path(rings, precision=0):
    parts = []
    for ring in rings:
        if len(ring) < 3:
            continue
        pts = [project(lon, lat) for lon, lat in ring]
        d = "M" + " L".join(f"{x:.{precision}f},{y:.{precision}f}" for x, y in pts) + " Z"
        parts.append(d)
    return " ".join(parts)


def main():
    countries = fetch_json(COUNTRIES_URL)
    land = fetch_json(LAND_URL)

    land_rings = []
    for geom in land["objects"]["land"]["geometries"]:
        land_rings.extend(geometry_rings(geom, land["arcs"], land["transform"]))
    land_path = rings_to_path(land_rings)

    by_name = {g["properties"]["name"]: g for g in countries["objects"]["countries"]["geometries"]}
    out_paths = {}
    for code, names in NAME_TARGETS.items():
        rings = []
        missing = [n for n in names if n not in by_name]
        if missing:
            print(f"WARNING: {code} missing names in source data: {missing}")
        for n in names:
            geom = by_name.get(n)
            if geom:
                rings.extend(geometry_rings(geom, countries["arcs"], countries["transform"]))
        out_paths[code] = rings_to_path(rings)
        print(f"{code}: {len(rings)} rings, {len(out_paths[code])} chars")

    out_path = Path(__file__).resolve().parent / "_world_geo_data.py"
    with out_path.open("w", encoding="utf-8") as f:
        f.write('"""Auto-generated equirectangular SVG path data.\n\n')
        f.write("Source: unpkg.com/world-atlas@2 (Natural Earth 110m via d3/topojson-project,\n")
        f.write("ISC-licensed conversion of public-domain Natural Earth data). Converted with\n")
        f.write("scripts/_build_world_geo_data.py's one-time build step (see that file to\n")
        f.write("regenerate; requires network access to unpkg.com, not needed at\n")
        f.write("report-build/view time).\n")
        f.write(f"Projected onto a {PLOT_W:.0f}x{PLOT_H:.0f} equirectangular plot area (lon -180..180\n")
        f.write(f"-> x 0..{PLOT_W:.0f}, lat 90..-90 -> y 0..{PLOT_H:.0f}); wrap in\n")
        f.write('<g transform="translate(L,T)"> to place.\n"""\n\n')
        f.write(f"PLOT_W = {PLOT_W:.0f}\nPLOT_H = {PLOT_H:.0f}\n\n")
        f.write(f'LAND_PATH = "{land_path}"\n\n')
        f.write("JURISDICTION_PATHS = {\n")
        for code, d in out_paths.items():
            f.write(f'    "{code}": "{d}",\n')
        f.write("}\n\n")
        f.write("LABEL_POINTS = {\n")
        for code, (lon, lat) in LABEL_LONLAT.items():
            x, y = project(lon, lat)
            f.write(f'    "{code}": ({x:.1f}, {y:.1f}),\n')
        f.write("}\n")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
