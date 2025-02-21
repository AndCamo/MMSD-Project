from geopy.geocoders import Nominatim
import csv
import pandas as pd
from geopy import distance
import pickle
geolocator = Nominatim(user_agent="progetto_mmsd")


# Dictionary data structure to save calculated addresses
distance_cache = {}

def calculate_distances():

    aule_dataframe = pd.read_csv("Data/classroom_dataset.csv", sep=";")
    corsi_dataframe = pd.read_csv("Data/degree_dataset.csv", sep=";")

    for index1, degree in corsi_dataframe.iterrows():
        for index2, room in aule_dataframe.iterrows():

            # defining a sorted tuple for consistency
            key = tuple(sorted([str(room["Indirizzo"]), degree["Sede Dipartimento"]]))

            #check if the distance was already calculated
            if key in distance_cache:
                print(f"[Retrived] {key}: {distance_cache[key]}")
                continue
            else:
                try:
                    room_location = str(room["Coordinate"]).split(", ")
                    degree_location = str(degree["Coordinate"]).split(", ")
                    dist = distance.distance((room_location[0], room_location[1]),
                                             (degree_location[0], degree_location[1])).km

                    distance_cache[key] = round(dist, 2)
                    print(f"[Calculated] {key}: {distance_cache[key]}")
                except:
                    print(f"Errore nel calcolo di: {key}")
                    distance_cache[key] = None




def salva_csv(dictionary, filename="distanze.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Address1", "Address2", "Distance"])  # Intestazione
        for (addr1, addr2), distanza in dictionary.items():
            writer.writerow([addr1, addr2, distanza])


def serialize_distance_dictionary(dictionary):
    with open("distance_dictionary.pkl", "wb") as file:
        pickle.dump(dictionary, file)

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

#calculate_distances()
#serialize_distance_dictionary(distance_cache)
#salva_csv(distance_cache)



#dataframe = pd.read_csv("Data/classroom_dataset.csv", sep=";")

#print(dataframe.info())
