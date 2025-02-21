import pandas as pd
import numpy as np
from pyomo.environ import *
from distance import get_distance, load_distance_dictionary



# ================= VARIABLE INDEX =================
ATTENDANCE_RATE = 0.6  # 60% of students attend classes
WEEKLY_HOURS = 40  # Hours available per classroom per week
MORNING_HOURS = 4  # Hours available in the morning
EVENING_HOURS = 4  # Hours available in the evening
SUBCOURSES_PER_COURSE = 3  # Number of subcourses per course
SUBCOURSE_CLASS_HOURS = 20  # Required classroom hours per subcourse per week
SUBCOURSE_LAB_HOURS = 0  # Required lab hours per subcourse per week

# ================= LOAD CLASSROOM DATA =================
df_rooms = pd.read_csv("Data/classroom_dataset.csv", sep=";")

A = df_rooms["Code"].tolist()  # List of all classrooms
L = df_rooms[df_rooms["aulaInformatica"] == 1]["Code"].tolist()  # List of computer labs
R = df_rooms[df_rooms["aulaInformatica"] == 0]["Code"].tolist()  # List of regular classrooms

s = dict(zip(df_rooms["Code"], df_rooms["Capienza"]))  # Classroom capacities
h = dict(zip(df_rooms["Code"], np.full(len(df_rooms), WEEKLY_HOURS)))  # Available hours per week

