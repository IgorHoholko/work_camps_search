"""
 File name   : utils.py
 Description : description

 Date created : 05.04.2021
 Author:  Ihar Khakholka
"""

from lxml import etree
from tqdm import tqdm
from typing import List, Tuple
import pandas as pd
import time
import numpy as np
import requests
from pandas._libs.tslibs.timedeltas import Timedelta
from pandas._libs.tslibs.timestamps import Timestamp


def parseProjectsUrls(tree: etree._Element) -> List[str]:
    return tree.xpath("/html/body/div[1]/section/div[1]/div/div/div[2]/div[2]/article/div/div[2]/div/div/a/@href")


def parseCountries(tree: etree._Element) -> List[str]:
    countries = tree.xpath(
        "/html/body/div[1]/section/div[1]/div/div/div[2]/div[2]/article/div/div[1]/div[1]/h4/small[2]/b/font")
    countries = [c.text.strip() for c in countries]
    return countries


def parseCities(tree: etree._Element) -> List[str]:
    cities = tree.xpath(
        "/html/body/div[1]/section/div[1]/div/div/div[2]/div[2]/article/div/div[1]/div[1]/h4/small[2]/text()")
    cities = [c.strip().split(',')[0] for c in cities]
    return cities


def parseDates(tree: etree._Element) -> Tuple[List[Timestamp], List[Timestamp], List[Timedelta]]:
    dates = tree.xpath("/html/body/div[1]/section/div[1]/div/div/div[2]/div[2]/article/div/div[1]/div[1]/h4/b/text()")
    dates_in = [pd.to_datetime(date.split('-')[0].strip(), dayfirst=True) for date in dates]
    dates_out = [pd.to_datetime(date.split('-')[-1].strip(), dayfirst=True) for date in dates]
    durations = [do - di for di, do in zip(dates_in, dates_out)]
    return dates_in, dates_out, durations


def parseNeeded(tree: etree._Element) -> Tuple[List[int], List[int], List[int]]:
    needed_raw = tree.xpath("/html/body/div[1]/section/div[1]/div/div/div[2]/div[2]/article/div/div[2]/p/text()")
    needed = []
    check = False
    sub_line = []
    for line in needed_raw:
        if check:
            sub_line.append(line)
            check = False
        if "Male" in line:
            check = True
            sub_line.append(line)
        if not check and len(sub_line):
            needed.append(sub_line)
            sub_line = []

    need_male = []
    need_female = []
    need_total = []
    for i, line in enumerate(needed):
        need_male.append(int(line[0].strip().split('\n')[0].split()[0]))
        need_female.append(int(line[0].strip().split('\n')[-1].split()[0]))
        need_total.append(int(line[1].split(':')[-1].strip()))
    return need_male, need_female, need_total


def parseProjectCodes(tree: etree._Element) -> List[str]:
    codes = tree.xpath("/html/body/div[1]/section/div[1]/div/div/div[2]/div[2]/article/div/div[1]/div[1]/h4/small[1]")
    codes = [c.text for c in codes]
    return codes


def parseProjectNames(tree: etree._Element) -> List[str]:
    names_raw = tree.xpath("/html/body/div[1]/section/div[1]/div/div/div[2]/div[2]/article/div/div[1]/div[1]/h4/text()")
    names = [line.strip() for line in names_raw if len(line)>3]
    return names


def parseProjectDescriptions(projects_urls: List[str], safe_mode: bool = True) -> Tuple[List[str], List[dict]]:
    raw_descs = []

    for url in tqdm(projects_urls):
        if safe_mode:
            time.sleep(np.random.rand())
        r = requests.get(url, headers={'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1)"
                                                     " AppleWebKit/537.36 (KHTML, like Gecko) "
                                                     "Chrome/89.0.4389.114 Safari/537.36"})
        td = etree.HTML(r.content)
        raw_descs.append(td.xpath("/html/body/div[1]/section/div/div/div[1]/div[2]/div/div[1]/div[2]/ul")[0])

    descriptions_dicts = []
    descriptions_full_text = []
    for line in raw_descs:
        titles = []
        sections = []
        for li in line.findall('li'):
            try:
                titles.append(li.find('label').text)
            except:
                sections.append(li.text)
        descriptions_dicts.append({title: section for title, section in zip(titles, sections)})
        try:
            descriptions_full_text.append("\n\t".join(sections))
        except:
            descriptions_full_text.append('')

    return descriptions_full_text, descriptions_dicts


def splitDescriptionsDicts(descriptions_dicts: List[dict]) \
        -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
    partner = []
    work = []
    accomodation = []
    location = []
    requarements = []
    for d in descriptions_dicts:
        if d["PARTNER"]:
            partner.append(d["PARTNER"])
            work.append(d["WORK"])
            accomodation.append(d["ACCOMODATION AND FOOD"])
            location.append(d["LOCATION & LEISURE ACTIVITY"])
            requarements.append(d["REQUIREMENTS"])
        else:
            partner.append(None)
            work.append(None)
            accomodation.append(None)
            location.append(None)
            requarements.append(None)
    return partner, work, accomodation, location, requarements