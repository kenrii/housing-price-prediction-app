import pgeocode
import numpy as np


def find_nearest_postal_code(postal_code, json):
    nomi = pgeocode.Nominatim("fi")
    location = nomi.query_postal_code([postal_code])
    latitude, longitude = location.latitude, location.longitude
    json_latitude, json_longitude = json["latitude"], json["longitude"]

    nearest_postal_code = "00100"
    min_distance = np.float("inf")
    for pc in json_latitude.keys():
        distance = _min_euclidean_distance(latitude, longitude, float(json_latitude[pc]), float(json_longitude[pc]))
        if distance < min_distance:
            min_distance = distance
            nearest_postal_code = pc

    return nearest_postal_code


def _min_euclidean_distance(pc_latitude, pc_longitude, candidate_latitude, candidate_longitude):
    distance = np.square(candidate_latitude - pc_latitude) + np.square(candidate_longitude - pc_longitude)
    return distance[0]
