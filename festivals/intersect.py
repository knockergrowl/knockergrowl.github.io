#!/usr/bin/python3

import argparse
import re
import sys

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')
# Required positional argument
parser.add_argument('-f', '--festivals', nargs='+', default=[], help='Festivals to include in the intersection', required=True)
parser.add_argument('-x', '--excluded', nargs='+', default=[], help='Festivals to filter out', required=False)
parser.add_argument('-m', '--min', nargs='?', type=int, default=0, help='Min occurrences of the band', required=False)
parser.add_argument('-n', '--normalise', action='store_true', help='Normalise names of bands to lowercase alphanumerical.')


def get_bands_from_file(file_path, normalise):
    bands= []
    with open(file_path, 'r', encoding='UTF-8') as file:
        for line in file:
            if not line.startswith('#') and line.strip().startswith('*'):
                raw_band_name = line.strip().split('* ')[-1]
                band_name = raw_band_name.lower() if normalise else raw_band_name
                bands.append(band_name)
    return bands

def get_title_from_file(file_path, fallback):
    try:
        with open(file_path, 'r', encoding='UTF-8') as file:
            for line in file:
                if line.startswith('# '):
                    return line.strip().split('# ')[-1]
    except:
        return fallback
    return fallback

def parse_festivals_per_band(festivals, normalise):
    bands = {}
    for fest in festivals:
        path = fest + '/bands-by-day.md'
        fest_bands = get_bands_from_file(path, normalise)
        for band in fest_bands:
            if not band in bands.keys():
                bands[band] = [fest]
            else:
                bands[band] = list(set(bands[band] + [fest]))
    return bands

def parse_festival_titles(festivals):
    titles = {}
    for fest in festivals:
        path = fest + '/README.md'
        title = get_title_from_file(path, fest)
        titles[fest] = title
    return titles

def build_markdown_table(fest_titles, bands, excluded_bands, min_occurrences):
    table = '| |' + '|'.join(map(lambda a: fest_titles[a], fest_titles.keys()))  + '|\n'
    table += '|---|' + '|'.join(['---'] * len(fest_titles.keys())) + '|\n'
    for band in sorted(bands.keys()):
        if band not in excluded_bands and len(bands[band]) >= min_occurrences :
          table += '|' + band + '|'
          for fest in fest_titles.keys():
              if fest in bands[band]:
                  table += 'Yes'
              else:
                  table += ''
              table += '|'
          table += '\n'
    return table

if __name__ == "__main__":
    args = parser.parse_args()
    bands = parse_festivals_per_band(args.festivals, args.normalise)
    print(f'Bands: {len(bands.keys())}', file=sys.stderr)
    excluded_bands = list(parse_festivals_per_band(args.excluded, args.normalise).keys())
    print(f'Excluded: {excluded_bands}', file=sys.stderr)
    fest_titles = parse_festival_titles(args.festivals)
    md_table = build_markdown_table(fest_titles, bands, excluded_bands, args.min)
    print(md_table.encode('utf-8').decode(sys.stdout.encoding))
