#!/usr/bin/env python3

import overpy
from yaml import dump
try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper
import click


def clean_way_tags(tags):
    if 'lanes' in tags:
        tags['lanes'] = int(tags['lanes'])

    if 'oneway' in tags:
        tags['oneway'] = tags['oneway'] == 'yes'

    return tags


@click.command()
@click.argument('city')
@click.argument('outfile', type=click.File('w'))
@click.option('--limit', type=click.IntRange(min=1), default=None,
              help="Limit the query to the first number of results "
                   "(default: no limit)")
def download_city_ways(city, outfile, limit):
    api = overpy.Overpass()
    q = 'area["name"~"{:s}"];way["highway"](area);out;'.format(city)
    results = api.query(q)

    ways = {}
    for i, way in enumerate(results.ways):
        w = clean_way_tags(way.tags)
        lats = []
        lons = []
        node_ids = []
        nodes = way.get_nodes(resolve_missing=True)
        for node in nodes:
            node_ids.append(node.id)
            lats.append(float(node.lat))
            lons.append(float(node.lon))

        w['nodes'] = {'ids': node_ids, 'lats': lats, 'lons': lons}
        ways[way.id] = w

        if limit and i >= limit:
            break

    dump(ways, outfile, Dumper=Dumper)


if __name__ == '__main__':
    download_city_ways()
