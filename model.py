import pandas as pd
import numpy as np
from pyomo.environ import *
from distance import get_distance, load_distance_dictionary

# ================= VARIABLE INDEX =================
WEEKLY_HOURS = 40  # Hours available per classroom per week
MORNING_HOURS = 4  # Hours available in the morning
EVENING_HOURS = 4  # Hours available in the evening
MAX_STUDENTS_PER_CLASS = 180 # Maximum students allowed per subcourse
LAB_PERCENTAGE = 0.25  # Percentage of time dedicated to lab classes
WEEK_NUMBER = 12  # Number of weeks in a semester

# CFU values per degree type
CFU_VALUES = {"I": 180, "II": 120, "CU": 300}
YEARS_PER_TYPE = {"I": 3, "II": 2, "CU": None}

# Attendance rate
ATTENDANCE_RATES = {
    "I": {1: 0.8, 2: 0.7, 3: 0.6},  # Bachelor's (I)
    "II": {1: 0.8, 2: 0.7},         # Master's (II)
    "CU": {1: 0.8, 2: 0.75, 3: 0.7, 4: 0.65, 5: 0.65, 6: 0.65}  # CU Attendance rates for 5/6 years
}

# ======================= LOAD CLASSROOM DATA =======================
df_rooms = pd.read_csv("Data/classroom_dataset.csv", sep=";")

A = df_rooms["Code"].tolist()  # List of all classrooms
L = df_rooms[df_rooms["aulaInformatica"] == 1]["Code"].tolist()  # List of computer labs
R = df_rooms[df_rooms["aulaInformatica"] == 0]["Code"].tolist()  # List of regular classrooms

s = dict(zip(df_rooms["Code"], df_rooms["Capienza"]))  # Classroom capacities
h = dict(zip(df_rooms["Code"], np.full(len(df_rooms), WEEKLY_HOURS)))  # Available hours per week

# ================= LOAD COURSE DATA =================
df_courses = pd.read_csv("Data/degree_dataset.csv", sep=";")

C = df_courses["COD"].tolist()  # List of courses
n = dict(zip(df_courses["COD"], df_courses["Participants"]))  # Number of students per course
course_levels = dict(zip(df_courses["COD"], df_courses["Livello"]))  # Course levels (I, II, CU)

# ================= LOAD DISTANCE DATA =================
distance_cache = load_distance_dictionary("Data/distance_dictionary.pkl")

# ================= CREATE CFU DISTRIBUTION =================
Y = {c: [] for c in C}  # Dictionary to store subcourses (and sub-subcourses)
n_y = {c: {} for c in C}  # Dictionary to store student numbers
cfu_y = {c: {} for c in C}  # Dictionary to store CFU for each subcourse/sub-subcourse
class_hours_y = {c: {} for c in C}  # Dictionary to store required class hours per week
attendance_rate_y = {c: {} for c in C} # Dictionary to store attendance rate for each subcourse/sub-subcourse

for c in C:
    level = course_levels[c]  # Get course level (I, II, CU)
    total_cfu = CFU_VALUES[level] 

    # Determine the number of subcourses based on level
    if level == "I":
        num_years = YEARS_PER_TYPE[level]
        cfu_per_subcourse = total_cfu / num_years 
        num_subcourses = 3
    elif level == "II":
        num_years = YEARS_PER_TYPE[level]
        cfu_per_subcourse = total_cfu / num_years 
        num_subcourses = 2
    else:
        cfu_per_subcourse = 60
        num_subcourses = total_cfu / 60  

    # Create subcourses
    subcourses = [f"{c}_Y{i+1}" for i in range(int(num_subcourses))]

    for i, y in enumerate(subcourses):
        year = i + 1

        num_students = round(n[c] / num_subcourses) if num_subcourses > 0 else n[c]

        if num_students > MAX_STUDENTS_PER_CLASS:
            num_subdivisions = -(-num_students // MAX_STUDENTS_PER_CLASS)  # Round up
            students_per_sub = num_students // num_subdivisions
            remainder = num_students % num_subdivisions

            for j in range(num_subdivisions):
                subsub_name = f"{y}_Z{j+1}"
                Y[c].append(subsub_name)
                n_y[c][subsub_name] = students_per_sub + (1 if j < remainder else 0)
                cfu_y[c][subsub_name] = cfu_per_subcourse  # Assign CFU
                class_hours_y[c][subsub_name] = (cfu_per_subcourse * 8 / WEEK_NUMBER) / 2 #divided by 2 semesters
                attendance_rate_y[c][subsub_name] = ATTENDANCE_RATES[level].get(year, 0.6)  # Default to 60% if missing
        else:
            Y[c].append(y)
            n_y[c][y] = num_students
            cfu_y[c][y] = cfu_per_subcourse  
            class_hours_y[c][y] = (cfu_per_subcourse * 8 / WEEK_NUMBER ) / 2 #divided by 2 semesters
            attendance_rate_y[c][y] = ATTENDANCE_RATES[level].get(year, 0.6)  # Default to 60% if missing

# ================= TIME SLOTS =================
T = ["M", "E"]
j = {"M": MORNING_HOURS, "E": EVENING_HOURS}
G = {"Mon", "Tue", "Wed", "Thu", "Fri"}
# ================= PYOMO MODEL =================
model = ConcreteModel()

# Decision Variables
model.x = Var([(a, y, c, g, t) for a in A for c in C for g in G for y in Y[c] for t in T], within=Binary)

# ================= CONSTRAINTS =================

# A classroom can be assigned to at most one sub-degree on a given day and time slot.
model.unique_assignment = ConstraintList()
for a in A:
    for g in G:
        for t in T:
            model.unique_assignment.add(sum(model.x[a, y, c, g, t] for c in C for y in Y[c]) <= 1)

# Constraint: Seat capacity must be sufficient for students attending the subcourse
model.seat_capacity = ConstraintList()
for c in C:
     for y in Y[c]:
         for a in A:
             for g in G:
                for t in T:
                    model.seat_capacity.add(model.x[a, y, c, g, t] * n_y[c][y] * attendance_rate_y[c][y] <= s[a])

# Constraint: Ensure required class hours are met
model.hour_request = ConstraintList()
for c in C:
    for y in Y[c]:
        model.hour_request.add(sum(j[t] * model.x[a, y, c, g, t] for a in A for g in G for t in T) >= class_hours_y[c][y] * (1 - LAB_PERCENTAGE))

# Constraint: Each subcourse must be assigned at least one classroom at some time slot
# model.forced_assignment = ConstraintList()
# for c in C:
#    for y in Y[c]:
#        model.forced_assignment.add(sum(model.x[a, y, c, g, t] for a in A for g in G for t in T) == 1)

# ================= OBJECTIVE FUNCTION =================
model.obj = Objective(expr=
    sum(model.x[a, y, c, g, t] * get_distance(df_courses.loc[df_courses["COD"] == c, "Sede Dipartimento"].values[0],
                                           df_rooms.loc[df_rooms["Code"] == a, "Indirizzo"].values[0],
                                           distance_cache)
        for a in A for c in C for y in Y[c] for g in G for t in T),
    sense=minimize)


# ================= SOLVE MODEL =================
solver = SolverFactory('cbc')
results = solver.solve(model, tee=True)

# Check Feasibility
if results.solver.termination_condition == TerminationCondition.infeasible:
    print("⚠️ The problem is infeasible! Adjust constraints.")
else:
    # Collect results
    allocation_results = []
    for (a, y, c, g, t) in model.x:
        if model.x[a, y, c, g, t].value == 1:  # If allocated

            # Compute the distance between the classroom and the department
            dept_location = df_courses.loc[df_courses["COD"] == c, "Sede Dipartimento"].values[0]
            classroom_location = df_rooms.loc[df_rooms["Code"] == a, "Indirizzo"].values[0]
            distance = get_distance(dept_location, classroom_location, distance_cache)

            new_result = {
                "Subclass Code" : y,
                "Degree Name" : df_courses.loc[df_courses["COD"] == c, "Denominazione CdS"].values[0],
                "Course Level" : course_levels[c],
                "Classroom ID" : a,
                "Day" : g,
                "Time Slot" : t,
                "Classroom Capacity" : s[a],
                "N.Attending Students" : round(n_y[c][y] * attendance_rate_y[c][y]),
                "N. Enrolled Students" : n_y[c][y],
                "Distance (km)" : distance,
                "Total Hour Request" : class_hours_y[c][y],
                "Normal Hours" : class_hours_y[c][y] * (1 - LAB_PERCENTAGE),
                "Lab Hours" : class_hours_y[c][y] * LAB_PERCENTAGE
            }


            allocation_results.append(list(new_result.values()))

    # Convert to DataFrame
    df_results = pd.DataFrame(allocation_results, columns=["Subclass Code", "Degree Name", "Course Level",
                                                           "Classroom ID", "Day", "Time Slot", "Classroom Capacity",
                                                           "N.Attending Students", "N. Enrolled Students", "Distance (km)",
                                                           "Total Hour Request", "Normal Hours", "Lab Hours"])

    # Save to Excel
    with pd.ExcelWriter("Classroom_Allocation.xlsx") as writer:
        df_results.to_excel(writer, sheet_name="Allocation", index=False)

    print("✅ Results saved to 'Classroom_Allocation.xlsx'")

