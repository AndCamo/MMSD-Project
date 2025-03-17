from geopy.geocoders import Nominatim
import csv
import pandas as pd
from geopy import distance
geolocator = Nominatim(user_agent="progetto_mmsd")


dataframe = pd.read_csv("Data/degree_dataset.csv", sep=";")
colonne = list(dataframe.keys())

new_dataframe = []

for index, row in dataframe.iterrows():
    if row["Modalita didattica"] == "convenzionale":
        new_dataframe.append(row)


df_new = pd.DataFrame(new_dataframe, columns=colonne)

df_new.to_csv("Data/degree_dataset_new.csv", index=False, sep=";")