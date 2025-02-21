from geopy.geocoders import Nominatim
import csv
import pandas as pd
from geopy import distance
import pickle
geolocator = Nominatim(user_agent="progetto_mmsd")

def load_distance_dictionary(filename):
    with open(filename, "rb") as file:
        return pickle.load(file)

def get_distance(address1, address2, dictionary):
    try:
        # defining a sorted tuple for consistency ( [address1, address2] = [address2, address1] )
        key = tuple(sorted([address1, address2]))
        distance = dictionary[key]
    except:
        # If the key does not exist, the average of the distances is returned.
        distance_sum = 0
        for item in dictionary.values():
            distance_sum += item

        distance = distance_sum / len(dictionary.values())


    return distance

distance_cache = load_distance_dictionary("Data/distance_dictionary.pkl")
print(get_distance("Via Sant'Ottavio, 54, Torino", "Palazzo Gorresio, via Giulia di Barolo 3/A, Torino", distance_cache))

