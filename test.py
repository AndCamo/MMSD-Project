from geopy.geocoders import Nominatim
import csv
import pandas as pd
from geopy import distance
geolocator = Nominatim(user_agent="progetto_mmsd")


dataframe = pd.read_csv("Data/classroom_dataset.csv", sep=";")


print(dataframe.to_json(orient="records"))