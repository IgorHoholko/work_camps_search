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

def findKeyWords(text: str, keywords: List[str]) -> List[str]:
    keyword_processor = KeywordProcessor()
    [keyword_processor.add_keyword(word) for word in keywords]
    keywords_found = []
    try:
        keywords_found = keyword_processor.extract_keywords(text)
    except:
        print(text)
    return keywords_found


def createPopup(df_row, tags_list: List[str]) -> folium.Popup:
    """ Get pandas row and transform it to folium Popup"""

    tags = [[tag.lower() for tag in tags] for tags in tags_list]

    html = open('app/templates/popup.html').read()
    template = Template(html)
    html = template.render(
        name=df_row["Name"],
        date_from = df_row['DateStart'], date_to = df_row['DateEnd'],
        males=df_row["NeedMale"], females=df_row["NeedFemale"], total=df_row["NeedTotal"],

        accomod= df_row["ACCOMODATION AND FOOD"],
        work = df_row["WORK"],
        location= df_row["LOCATION & LEISURE ACTIVITY"],
        requirements = df_row['REQUIREMENTS'],

        code=df_row['Code'],
        link=df_row['URL'],
        any_tags=bool(len(tags)),
        tags=tags
    )
    return folium.Popup(html,  max_width=800)

