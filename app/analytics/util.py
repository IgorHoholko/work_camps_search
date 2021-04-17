"""
 File name   : util.py
 Description : description

 Date created : 08.04.2021
 Author:  Ihar Khakholka
"""


from flashtext import KeywordProcessor
from typing import List
import folium
from jinja2 import Template
import pandas as pd
import calendar


def pdTimestamp2readable(date: pd.Timestamp) -> str:
    return "{} {} {}".format(date.day, calendar.month_abbr[date.month], date.year)

def pdSetDiff(df1: pd.DataFrame, df2: pd.DataFrame):
    """ df1 - df2 """
    return pd.concat([df2, df1, df1]).drop_duplicates(keep=False)


def findKeyWords(text: str, keywords: List[str]) -> List[str]:
    keyword_processor = KeywordProcessor()
    [keyword_processor.add_keyword(word) for word in keywords]
    keywords_found = []
    try:
        keywords_found = keyword_processor.extract_keywords(text)
    except:
        print(text)
    return keywords_found


def renderPopupHTML(df_row, tags: List[str] = None, in_saved: bool = False) -> folium.Popup:
    """ Get pandas row and transform it to folium Popup"""

    tags = tags if tags is not None else []
    tags = [tag.lower() for tag in tags]
    tags = set(tags)

    info_dict = df_row.to_dict()
    info_dict['DateStart'] = pdTimestamp2readable(info_dict['DateStart'])
    info_dict['DateEnd'] = pdTimestamp2readable(info_dict['DateEnd'])

    html = open('app/templates/popup.html').read()
    template = Template(html)
    html = template.render(
        info_dict = info_dict,
        any_tags=bool(len(tags)),
        tags=tags,
        in_saved = in_saved
    )
    return folium.Popup(html,  max_width=800)


def renderProjectsPageHTML(df: pd.DataFrame, tags_list: List[List[str]] = None,
                           saved_cache: List[str] = None, viewed_codes: List[str] = None) -> str:
    if tags_list:
        assert len(df) == len(tags_list)
    saved_cache = saved_cache if saved_cache is not None else []
    viewed_codes = viewed_codes if viewed_codes is not None else []

    headers = []
    info_dicts = []

    for j, (_, row) in enumerate(df.iterrows()):
        info_dict = row.to_dict()
        info_dict['DateStart'] = pdTimestamp2readable(info_dict['DateStart'])
        info_dict['DateEnd'] = pdTimestamp2readable(info_dict['DateEnd'])

        tags = tags_list[j] if tags_list is not None else []
        tags = [tag.lower() for tag in tags]
        tags = set(tags)
        info_dict['tags'] = tags
        info_dict['in_saved'] = row['Code'] in saved_cache
        info_dict['in_viewed'] = row['Code'] in viewed_codes

        headers.append("{}, {}".format(info_dict['Code'], info_dict['Country']))
        info_dicts.append(info_dict)


    html = open('app/templates/projects_page.html').read()
    template = Template(html)
    html = template.render(
        headers = headers,
        info_dicts = info_dicts,
        any_tags = tags_list is not None,
    )
    return html


