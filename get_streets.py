#!/usr/bin/env python3

import osmapi
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

api = osmapi.OsmApi()

detroit = api.RelationGet(134591)

max_lat = -180
min_lat = 180
max_lon = -360
min_lon = 360

for member in detroit['member']:
    if member['type'] != 'way' or member['role'] != 'outer':
        continue
    way = api.WayGet(member['ref'])
    if not way['visible']:
        continue
    nodes = api.NodesGet(way['nd'])
    for _, node in nodes.items():
        if node['lat'] < min_lat:
            min_lat = node['lat']
        if node['lon'] < min_lon:
            min_lon = node['lon']
        if node['lat'] > max_lat:
            max_lat = node['lat']
        if node['lon'] > max_lon:
            max_lon = node['lon']

streets = {}

# Can't download too many nodes at once, so slice this up
low_lon = min_lon
high_lon = min_lon + 0.01
while high_lon <= max_lon:
    low_lat = min_lat
    high_lat = min_lat + 0.01
    while high_lat <= max_lat:
        # print(low_lon, low_lat, high_lon, high_lat)
        maplet = api.Map(low_lon, low_lat, high_lon, high_lat)

        for node in maplet:
            if node['type'] != 'way':
                continue
            # print(node)
            data = node['data']
            node_id = data['id']
            tags = data['tag']
            if 'highway' not in tags:
                continue
            if 'name' not in tags or 'lanes' not in tags:
                #name = '(service drive)'
                continue
            else:
                name = tags['name']
                lanes = tags['lanes']
            nodes = data['nd']

            if node_id in streets:
                streets[node_id]['nodes'] += nodes
            else:
                streets[node_id] = {
                    'nodes': nodes,
                    'lanes': lanes,
                    'name': name
                }

        low_lat = high_lat
        high_lat += 0.01

    low_lon = high_lon
    high_lon += 0.01

print(dump(streets, Dumper=Dumper))
