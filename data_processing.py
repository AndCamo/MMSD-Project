from geopy.geocoders import Nominatim
import time
import pandas as pd
from geopy import distance
geolocator = Nominatim(user_agent="progetto_mmsd")

dataframe = pd.read_excel("Data/Elenco Aule - Usable.xlsx")


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

def get_building_usage():
    classroom_dataset = pd.read_csv("Data/classroom_dataset.csv", sep=";")
    result_dataset = pd.read_excel("Classroom_Allocation.xlsx")

    buildings = list(classroom_dataset["Edificio"].unique())


    # count the number of classroom in each building
    building_dimension = {b: len(classroom_dataset["Edificio"].loc[classroom_dataset["Edificio"] == b]) for b in buildings}

    # dict to count how many classroom are actually used
    building_usage = {b : 0 for b in buildings}

    unique_result_dataset = result_dataset.drop_duplicates(subset=["Classroom ID"])

    for index, row in unique_result_dataset.iterrows():
        classroom_assigned = row["Classroom ID"]
        classroom_assigned_building = classroom_dataset.loc[
            classroom_dataset["Code"] == classroom_assigned, "Edificio"].values[0]

        building_usage[classroom_assigned_building] += 1


    result_list = []
    for key, value in building_usage.items():
        new_row = [key, building_dimension[key], building_usage[key], (100 * building_usage[key])/building_dimension[key]]
        result_list.append(new_row)

    usage_dataframe = pd.DataFrame(result_list, columns=["Building", "Total Classrooms", "Used Classrooms", "Building Usage"])
    usage_dataframe.to_csv("usage.csv", index=False)

get_building_usage()