"""
 File name   : parser.py
 Description : description

 Date created : 05.04.2021
 Author:  Ihar Khakholka
"""

import lxml
from lxml import etree
import numpy as np
import argparse
import pandas as pd
from os.path import join
from .utils import (parse_cities, parse_dates, parse_needed, parse_countries, parse_project_codes,
                    parse_project_descriptions, parse_project_names, parse_projects_urls, split_descriptions_dicts)
from .geo_tools import get_coordinates

import os



def _parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", "-i", type=str, help="Path to html page", default="E-vet 2021 LYVS templete.html")
    parser.add_argument("--web", '-w', type=str, help="Web address", default=None)
    parser.add_argument("--output", '-o', type=str, help="Path to folder where to save results", default="./data")
    parser.add_argument("--safe_mode", type=bool, help="Safe mode for parsing", default=True)
    parser.add_argument("--advanced_search", type=bool, help = "If use advanced coordinates estimation", default=True)

    args = parser.parse_args()
    return args


def main():
    args = _parse_args()
    if not args.input and not args.web:
        raise ValueError("Specify HTML path or WEB URL of the page.")

    os.makedirs(args.output, exist_ok=True)

    with open("E-vet 2021 LYVS templete.html") as f:
        tree = lxml.etree.HTML(f.read())

    # Data parsing
    countries = parse_countries(tree)
    cities = parse_cities(tree)
    dates_in, dates_out, durations = parse_dates(tree)
    need_male, need_female, need_total = parse_needed(tree)
    project_codes = parse_project_codes(tree)
    names = parse_project_names(tree)
    projects_urls = parse_projects_urls(tree)

    descriptions_full_text, descriptions_dicts = parse_project_descriptions(projects_urls, args.safe_mode)
    descriptions_partner, descriptions_work, descriptions_accomodation,\
            descriptions_location, descriptions_requarements = split_descriptions_dicts(descriptions_dicts)

    full_adresses, latitudes, longitudes = get_coordinates(countries, cities, args.advanced_search, descriptions_dicts)

    # Save to pandas DataFrame
    data = [project_codes, names, dates_in, dates_out, durations, countries, cities, latitudes, longitudes,
            need_female, need_male, need_total, descriptions_full_text, projects_urls,
            descriptions_partner, descriptions_work, descriptions_accomodation, descriptions_location, descriptions_requarements]

    columns = ["Code", "Name", "DateStart", "DateEnd", "Duration", "Country", "City", "Latitude", "Lognitude",
               "NeedFemale", "NeedMale", "NeedTotal", "Description", "URL"] + list(descriptions_dicts[0].keys())
    data = np.array(data).T
    df = pd.DataFrame(data, columns=columns)

    df.to_csv(f"{args.output}/new_data.csv")


if __name__ == '__main__':
    main()
