from geopy.geocoders import Nominatim
import time
import pandas as pd
from geopy import distance
geolocator = Nominatim(user_agent="progetto_mmsd")

dataframe = pd.read_excel("Data/Elenco Aule - Usable Updated.xlsx")


def calculate_coordinates():


    addresses = dataframe["Indirizzo"].tolist()
    print(len(addresses))
    coordinates = []
    coordinates_cache = {}

    for address in addresses:
        if address in coordinates_cache:
            coordinates.append(coordinates_cache[address])
            print(f"[Retrived] {address}: {coordinates_cache[address]}")
        else:
            try:
                location = geolocator.geocode(address)
                if location is None:
                    raise Exception
                else:
                    new_coordinates = f"{location.latitude}, {location.longitude}"
                    coordinates.append(new_coordinates)
                    coordinates_cache[address] = new_coordinates
                    print(f"[Calculated] {address}: {coordinates_cache[address]}")
            except:
                new_coordinates = "0,0"
                coordinates.append(new_coordinates)
                coordinates_cache[address] = new_coordinates
                print(f"[Error] {address}: {coordinates_cache[address]}")

    return  coordinates


pippo = calculate_coordinates()
time.sleep(5)
dataframe.insert(4, 'Coordinate', pippo)

dataframe.to_csv("new_elenco_classroom.csv", encoding='utf-8', index=False)