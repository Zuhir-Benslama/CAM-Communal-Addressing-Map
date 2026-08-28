#!/usr/bin/env python3
"""Convert the communes pg_dump into a GeoPackage.

Reads the raw Postgres dump (template_data/replacements/communes_with_geom.sql,
gitignored because it is a 52MB text file) and writes a queryable, spatially
indexed GeoPackage layer. The dump stores attributes in a COPY block and the
boundaries as per-row ``ST_GeomFromText('POLYGON (...)')`` updates keyed by
``commune_code``, so both sections are parsed and joined on that code.
"""

import argparse
import re
from pathlib import Path

import pandas as pd
from geopandas import GeoDataFrame
from pyogrio import write_dataframe
from shapely.geometry import MultiPolygon
from shapely.wkt import loads

COPY_RE = re.compile(
    r'COPY public\.communes \(([^)]*)\) FROM stdin;\n(.*?)\\\.\n', re.S
)
GEOM_RE = re.compile(r"ST_GeomFromText\('([^']+)'[^)]*\) WHERE commune_code = (\d+)")


def parse_sql(path):
    raw = Path(path).read_text(encoding='utf-8')
    copy = COPY_RE.search(raw)
    if copy is None:
        raise ValueError('COPY block not found; is this the expected pg_dump?')
    cols = [col.strip() for col in copy.group(1).split(',')]
    lines = copy.group(2).rstrip('\n').split('\n')
    records = [dict(zip(cols, line.split('\t'), strict=True)) for line in lines]

    geoms = {}
    for wkt, code in GEOM_RE.findall(raw):
        geoms.setdefault(int(code), loads(wkt))
    return records, geoms


def to_dataframe(records, geoms):
    df = pd.DataFrame(records)
    for col in ('commune_id', 'daira_id', 'commune_code'):
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    for col in ('commune_latitude', 'commune_longitude'):
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['geometry'] = [geoms.get(code) for code in df['commune_code']]

    def normalize(g):
        if g is None or g.geom_type == 'MultiPolygon':
            return g
        return MultiPolygon([g])

    df['geometry'] = df['geometry'].map(normalize)
    return GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'source',
        default='template_data/replacements/communes_with_geom.sql',
        nargs='?',
        help='pg_dump file to read (default: %(default)s)',
    )
    parser.add_argument(
        'output',
        default='template_data/replacements/communes.gpkg',
        nargs='?',
        help='GeoPackage to write (default: %(default)s)',
    )
    args = parser.parse_args()

    records, geoms = parse_sql(args.source)
    gdf = to_dataframe(records, geoms)

    out = Path(args.output)
    write_dataframe(gdf, str(out), layer='communes', geometry_type='MultiPolygon')
    with_geom = int(gdf['geometry'].notna().sum())
    print(f'wrote {len(gdf)} rows ({with_geom} with geometry) to {out}')


if __name__ == '__main__':
    main()
