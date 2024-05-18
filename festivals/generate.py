#!/usr/bin/python3

import argparse
import re
import sys

# Instantiate the parser
parser = argparse.ArgumentParser(description='Optional app description')
# Required positional argument
parser.add_argument('folder', type=str, help='Folder to process')


def get_bands_by_dimension(file_path):
    bands = {}
    with open(file_path, 'r', encoding='UTF-8') as file:
        # Day or genre
        dimension = None
        for line in file:
            line = re.sub('[|].*', '', line).strip()
            if line.startswith("#### "):
                dimension = line.strip().split('# ')[-1]
                bands[dimension] = []
            elif line.strip().startswith("*"):
                bands[dimension].append(line.strip().split("* ")[-1])
    return bands

def build_band_maps(day_file, genre_file, tiers_file):
    bands_by_day = get_bands_by_dimension(day_file)
    bands_by_genre = get_bands_by_dimension(genre_file)
    bands_by_tier = get_bands_by_dimension(tiers_file)
    return bands_by_day, bands_by_genre, bands_by_tier

def get_band_format(band, bands_by_tier):
    if band in bands_by_tier.get("Headliner", []):
        return f"<span style=\"font-size: larger; font-weight: bold;\">{band}</span>"
    elif band in bands_by_tier.get("Second", []):
        return f"<span style=\"font-size: medium; font-weight: bold;\">{band}</span>"
    return band

def build_markdown_table(bands_by_day, bands_by_genre, bands_by_tier):
    genres = bands_by_genre.keys()
    days = bands_by_day.keys()

    table = "|Genre|" + "|".join(days) + "|\n"
    table += "|---|" + "|".join(["---"] * len(days)) + "|\n"

    for genre in genres:
        table += f"|_{genre}_|"
        for day in days:
            bands = bands_by_genre[genre]
            common_bands = set(bands).intersection(set(bands_by_day[day]))
            common_bands_formatted = [get_band_format(band, bands_by_tier) for band in common_bands]
            table += ", ".join(common_bands_formatted) if common_bands_formatted else "-"
            table += "|"
        table += "\n"
    return table

if __name__ == "__main__":
    args = parser.parse_args()
    day_file = args.folder + "/bands-by-day.md"
    genre_file = args.folder + "/bands-by-genre.md"
    tiers_file = args.folder + "/bands-by-tier.md"
    bands_by_day, bands_by_genre, bands_by_tier = build_band_maps(day_file, genre_file, tiers_file)
    markdown_table = build_markdown_table(bands_by_day, bands_by_genre, bands_by_tier)
    print(markdown_table.encode('utf-8').decode(sys.stdout.encoding))
