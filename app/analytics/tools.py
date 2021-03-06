"""
 File name   : tools.py
 Description : Tools for table manipulating

 Date created : 07.04.2021
 Author:  Ihar Khakholka
"""

import pandas as pd
from typing import Tuple, List, Union

from .util import findKeyWords, renderPopupHTML
from collections import defaultdict
from folium.plugins import MarkerCluster
from folium.map import Marker
import folium

class Analytics:

    @staticmethod
    def selectByTime(df: pd.DataFrame, time_from: str, time_to: str) -> pd.DataFrame:
        time_from = pd.to_datetime(time_from, dayfirst=True)
        time_to = pd.to_datetime(time_to, dayfirst=True)
        mask = (time_from <= df['DateStart']) & (df['DateStart'] <= time_to)
        return df[mask]


    @staticmethod
    def selectByKeywords(df: pd.DataFrame, keywords: list) -> Tuple[pd.DataFrame, List[List[str]]]:
        mask = []
        list_keywords_found = []
        for i, row in df.iterrows():
            keywords_found = findKeyWords(row['Description'], keywords)
            mask.append(bool(len(keywords_found)))
            if len(keywords_found):
                list_keywords_found.append(keywords_found)

        return df[mask], list_keywords_found


    @staticmethod
    def getMarkers(df: pd.DataFrame, list_keywords: List[List[str]] = None, saved_cache: List[str] = None,
                   viewed_codes: List[str] = None)  -> List[Union[Marker, MarkerCluster]]:
        list_keywords = list_keywords if list_keywords is not None else []
        saved_cache = saved_cache if saved_cache is not None else []
        viewed_codes = viewed_codes if viewed_codes is not None else []

        # df_ = df.dropna(subset=['Latitude'])

        markers_dict = defaultdict(list)
        for j, (i, row) in enumerate(df.iterrows()):
            if row['Code'] in saved_cache:
                color = 'green'
            elif row['Code'] in viewed_codes:
                color = 'lightgray'
            else:
                color = 'blue'
            latitude, lognitude = row['Latitude'], row["Lognitude"]
            if not pd.notna(latitude):
                continue
            if len(list_keywords):
                popup = renderPopupHTML(row, list_keywords[j], in_saved=(color=='green'))
            else:
                popup = renderPopupHTML(row, in_saved=(color=='green'))
            marker_carcase = {"location" :[latitude, lognitude],
                               "popup" : popup,
                               "icon" : folium.Icon(color=color, icon="info", prefix='fa')}
            markers_dict[(latitude, lognitude)].append(marker_carcase)

        markers = []
        for key, marker_carcases in markers_dict.items():
            if len(marker_carcases) == 1:
                markers.append(folium.Marker(**marker_carcases[0]))
            else:
                markers.append(MarkerCluster(
                    locations = [mc['location'] for mc in marker_carcases],
                    popups = [mc['popup'] for mc in marker_carcases],
                    icons = [mc['icon'] for mc in marker_carcases],
                ))
        return markers










