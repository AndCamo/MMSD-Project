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
    significative_classrooms = {
        b: len(classroom_dataset.loc[(classroom_dataset["Edificio"] == b) & (classroom_dataset["Capienza"] > 40)])
        for b in buildings
    }


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

        new_row = [key, building_dimension[key], significative_classrooms[key], building_usage[key], (100 * building_usage[key])/building_dimension[key]]
        result_list.append(new_row)

    usage_dataframe = pd.DataFrame(result_list, columns=["Building", "Total Classrooms", "Significative Classrooms (seats>40)" ,"Used Classrooms", "Building Usage"])
    usage_dataframe.to_csv("usage.csv", index=False)


def get_assignments_stats():
    degree_dataset = pd.read_csv("Data/degree_dataset.csv", sep=";")
    result_dataset = pd.read_excel("Classroom_Allocation.xlsx")
    ranges = [tuple(sorted([0, 0.5])), tuple(sorted([0.5, 1])), tuple(sorted([1, 2])), tuple(sorted([2, 3])),
              tuple(sorted([3, 4])), tuple(sorted([4, 5])), tuple(sorted([5, 20]))]
    range_counter = {r: 0 for r in ranges}

    stats = []

    for j, degree in degree_dataset.iterrows():
        distance_sum = 0
        range_counter = {r : 0 for r in ranges}
        assignments_for_degree = result_dataset[result_dataset["Subclass Code"].str.contains(degree["COD"], na=False)]
        for i, assignment in assignments_for_degree.iterrows():
            distance = assignment["Distance (km)"]
            distance_sum += distance
            for range in range_counter.keys():
                if range[0] <= distance < range[1]:
                    range_counter[range] += 1
                    break

        degree_code = degree["COD"]
        degree_name = degree["Denominazione CdS"]
        degree_students = degree["Participants"]
        degree_department = degree["Dipartimento"]
        degree_level =  degree["Livello"]
        n_assignments = assignments_for_degree.shape[0]
        distance_mean = round(distance_sum /  n_assignments, 2)

        new_stat = [degree_code, degree_name, degree_department, degree_level, degree_students, n_assignments, distance_mean]
        new_stat.extend(range_counter.values())

        stats.append(new_stat)

    dataframe_columns = ["Degree Code", "Degree Name", "Degree Department" , "Degree Level", "Number of Students", "Number of Assignments", "Mean Distance"]
    dataframe_columns.extend(range_counter.keys())

    stats_dataframe = pd.DataFrame(stats, columns=dataframe_columns)
    stats_dataframe.to_csv("Stats/assignment_stats.csv", index=False)


def count_degree_in_department():

    complete_degree_dataset = pd.read_csv("Data/degree_dataset.csv", sep=";")
    degree_dataset = complete_degree_dataset[complete_degree_dataset["Modalita didattica"] == "convenzionale"]

    department_headquarters =  list(degree_dataset["Sede Dipartimento"].unique())


    degree_in_department = []


    for headquarter in department_headquarters:
        degree_subset = degree_dataset.loc[degree_dataset["Sede Dipartimento"] == headquarter]
        tmp_list = [list(degree_subset["Dipartimento"].unique()), degree_subset.iloc[0]["Sede Dipartimento"], degree_subset.shape[0]]
        degree_in_department.append(tmp_list)

    degree_in_department_dataframe = pd.DataFrame(degree_in_department, columns=["Dipartimento", "Sede", "Numero Lauree"])
    degree_in_department_dataframe.to_csv("Stats/degree_in_department.csv", index=False)