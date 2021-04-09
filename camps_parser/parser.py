"""
 File name   : parser.py
 Description : description

 Date created : 05.04.2021
 Author:  Ihar Khakholka
"""
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)


import lxml
from lxml import etree
import numpy as np
import argparse
import pandas as pd
from os.path import join
from parser.utils import (parseCities, parseDates, parseNeeded, parseCountries, parseProjectCodes,
                    parseProjectDescriptions, parseProjectNames, parseProjectsUrls, splitDescriptionsDicts)
from parser.geo_tools import getCoordinates

import os


def parsePage(input_page: str, safe_mode: bool, advanced_search: bool) -> pd.DataFrame:

    with open(input_page) as f:
        tree = lxml.etree.HTML(f.read())

    # Data parsing
    countries = parseCountries(tree)
    cities = parseCities(tree)
    dates_in, dates_out, durations = parseDates(tree)
    need_male, need_female, need_total = parseNeeded(tree)
    project_codes = parseProjectCodes(tree)
    names = parseProjectNames(tree)
    projects_urls = parseProjectsUrls(tree)

    descriptions_full_text, descriptions_dicts = parseProjectDescriptions(projects_urls, safe_mode)
    descriptions_partner, descriptions_work, descriptions_accomodation,\
            descriptions_location, descriptions_requarements = splitDescriptionsDicts(descriptions_dicts)

    full_adresses, latitudes, longitudes = getCoordinates(countries, cities, advanced_search, descriptions_dicts)

    # Save to pandas DataFrame
    data = [project_codes, names, dates_in, dates_out, durations, countries, cities, latitudes, longitudes,
            need_female, need_male, need_total, descriptions_full_text, projects_urls,
            descriptions_partner, descriptions_work, descriptions_accomodation, descriptions_location, descriptions_requarements]

    columns = ["Code", "Name", "DateStart", "DateEnd", "Duration", "Country", "City", "Latitude", "Lognitude",
               "NeedFemale", "NeedMale", "NeedTotal", "Description", "URL"] + list(descriptions_dicts[0].keys())
    data = np.array(data).T
    df = pd.DataFrame(data, columns=columns)

    return df


