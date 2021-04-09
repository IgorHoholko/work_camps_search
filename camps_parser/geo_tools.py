"""
 File name   : geo_tools.py
 Description : description

 Date created : 05.04.2021
 Author:  Ihar Khakholka
"""

from typing import Tuple, List
from tqdm import tqdm
from geotext import GeoText
from geopy.geocoders import Nominatim

def getCoordinates(countries: List[str], cities: List[str],
                    advanced_search = False, descriptions_dicts: List[dict] = None) \
    -> Tuple[List[str], List[float], List[float]]:

    if advanced_search and descriptions_dicts is None:
        raise ValueError("Send descriptions for advanced search.")

    geolocator = Nominatim(user_agent="Test")

    full_adresses = []
    latitudes = []
    longitudes = []

    for city, country in tqdm(zip(cities, countries), total=len(cities), desc="Coordinates estimation.."):
        if city != '-':
            try:
                address = f'{city}, {country}'
                location = geolocator.geocode(address)
                full_adresses.append(location.address)
                latitudes.append(location.latitude)
                longitudes.append(location.longitude)
            except:
                full_adresses.append(None)
                latitudes.append(None)
                longitudes.append(None)
        else:
            full_adresses.append(None)
            latitudes.append(None)
            longitudes.append(None)

    # Advanced Search
    if advanced_search:
        for i in tqdm(range(len(full_adresses)), desc="Missed coordinates Advanced Estimation.."):
            if full_adresses[i] is not None:
                continue

            detected_cities = []
            try:
                places = GeoText(descriptions_dicts[i]["LOCATION & LEISURE ACTIVITY"])
                if not len(places.cities):
                    places = GeoText(descriptions_dicts[i]["ACCOMODATION AND FOOD"])
                if not len(places.cities):
                    places = GeoText(descriptions_dicts[i]["WORK"])
                detected_cities = places.cities
            except:
                pass
            if len(detected_cities):
                address = f'{detected_cities[0]}, {cities[i]}'
                location = geolocator.geocode(address)

                latitudes[i] = location.latitude
                longitudes[i] = location.longitude
                full_adresses[i] = address + " (AS)"
    return full_adresses, latitudes, longitudes
