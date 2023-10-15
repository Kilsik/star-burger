import requests

from django.shortcuts import render
from django.conf import settings
from geopy import distance

from .models import Location


def fetch_coordinates(apikey, address):
    try:
        location = Location.objects.get(address=address)
        lon = location.longitude
        lat = location.latitude
    except Location.DoesNotExist:
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        location = Location.objects.create(address=address,
                                           latitude=lat,
                                           longitude=lon)
        location.save()
    return lat, lon


def calc_distances(restaurants, address):
    client_coord = fetch_coordinates(settings.GEO_KEY, address)
    if not client_coord:
        return None
    with_distance = []
    for restaurant in restaurants:
        restaurant_coord = fetch_coordinates(settings.GEO_KEY, restaurant.address)
        delivery_distance = round(distance.distance(restaurant_coord, client_coord).km, 3)
        with_distance.append(
            {'name': restaurant.name,
             'distance': delivery_distance}
        )
    return sorted(with_distance, key=lambda d: d['distance'])
