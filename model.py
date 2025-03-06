import pandas as pd
import numpy as np
from pyomo.environ import *
from distance import get_distance, load_distance_dictionary


# ================= VARIABLE INDEX =================
WEEKLY_HOURS = 40  # Hours available per classroom per week
MORNING_HOURS = 4 * 5  # Hours available in the morning
EVENING_HOURS = 4 * 5  # Hours available in the evening
SUBCOURSE_CLASS_HOURS = 20  # Required classroom hours per subcourse per week
SUBCOURSE_LAB_HOURS = 0  # Required lab hours per subcourse per week
MAX_STUDENTS_PER_CLASS = 250  # Maximum students allowed per subcourse

# CFU values per degree type
CFU_VALUES = {"I": 180, "II": 120, "CU": 20}
YEARS_PER_TYPE = {"I": 3, "II": 2, "CU": 1}

# Attendence rate
ATTENDANCE_RATES = {
    "I": {1: 0.8, 2: 0.7, 3: 0.6},  # Bachelor's (I)
    "II": {1: 0.7, 2: 0.6},         # Master's (II)
    "CU": {1: 0.8}                   # CU (one-year program)
}

# ================= LOAD CLASSROOM DATA =================
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

for c in C:
    level = course_levels[c]  # Get course level (I, II, CU)
    total_cfu = CFU_VALUES[level]
    num_years = YEARS_PER_TYPE[level]
    cfu_per_subcourse = total_cfu / num_years  

    # Determine the number of subcourses based on level
    if level == "I":
        num_subcourses = 3
    elif level == "II":
        num_subcourses = 2
    else:
        num_subcourses = 0  

    # Create subcourses
    subcourses = [f"{c}_Y{i+1}" for i in range(num_subcourses)]

    for i, y in enumerate(subcourses):
        year = i + 1  # Year 1, 2, or 3
        attendance_rate = ATTENDANCE_RATES[level].get(year, 0.6)  # Default to 60% if missing
        num_students = round(n[c] * attendance_rate / num_subcourses) if num_subcourses > 0 else round(n[c] * attendance_rate)

        if num_students > MAX_STUDENTS_PER_CLASS:
            num_subdivisions = -(-num_students // MAX_STUDENTS_PER_CLASS)  # Round up
            students_per_sub = num_students // num_subdivisions
            remainder = num_students % num_subdivisions

            for j in range(num_subdivisions):
                subsub_name = f"{y}_Z{j+1}"
                Y[c].append(subsub_name)
                n_y[c][subsub_name] = students_per_sub + (1 if j < remainder else 0)
                cfu_y[c][subsub_name] = cfu_per_subcourse  # Assign CFU
        else:
            Y[c].append(y)
            n_y[c][y] = num_students
            cfu_y[c][y] = cfu_per_subcourse  

    # If no subcourses exist (CU type), enforce max class size
    if num_subcourses == 0:
        attendance_rate = ATTENDANCE_RATES[level][1]  # Only one year in CU
        num_students = round(n[c] * attendance_rate)

        if num_students > MAX_STUDENTS_PER_CLASS:
            num_subdivisions = -(-num_students // MAX_STUDENTS_PER_CLASS)
            students_per_sub = num_students // num_subdivisions
            remainder = num_students % num_subdivisions

            for j in range(num_subdivisions):
                sub_name = f"{c}_Z{j+1}"
                Y[c].append(sub_name)
                n_y[c][sub_name] = students_per_sub + (1 if j < remainder else 0)
                cfu_y[c][sub_name] = total_cfu  
        else:
            Y[c].append(c)
            n_y[c][c] = num_students
            cfu_y[c][c] = total_cfu

# ================= TIME SLOTS =================
T = ["M", "E"]
g = {"M": MORNING_HOURS, "E": EVENING_HOURS}

# ================= PYOMO MODEL =================
model = ConcreteModel()

# Decision Variables
model.x = Var([(a, y, c, t) for a in A for c in C for y in Y[c] for t in T], within=Binary)

# ================= CONSTRAINTS =================

# Constraint: Ensure no room is double-booked at the same time
# model.unique_assignment = ConstraintList()
# for a in A:
#     for t in T:
#         model.unique_assignment.add(sum(model.x[a, y, c, t] for c in C for y in Y[c]) <= 1)

# Constraint: Seat capacity must be sufficient for students attending the subcourse
# model.seat_capacity = ConstraintList()
# for c in C:
#     for y in Y[c]:
#         for a in A:
#             for t in T:
#                 model.seat_capacity.add(model.x[a, y, c, t] * n_y[c][y] <= s[a])

# # Constraint: Ensure required class and lab hours are met
# model.hour_request = ConstraintList()
# for c in C:
#     for y in Y[c]:
#         model.hour_request.add(sum(g[t] * model.x[a, y, c, t] for a in A for t in T) >= SUBCOURSE_CLASS_HOURS)
        #model.hour_request.add(sum(g[t] * model.x[a, y, c, t] for a in R for t in T) + model.delta_u[y, c] <= SUBCOURSE_CLASS_HOURS + 3)
        #model.hour_request.add(sum(g[t] * model.x[a, y, c, t] for a in L for t in T) + model.delta_q[y, c] >= SUBCOURSE_LAB_HOURS)
        #model.hour_request.add(sum(g[t] * model.x[a, y, c, t] for a in R for t in T) + model.delta_u[y, c] <= SUBCOURSE_LAB_HOURS + 3)

# Constraint: Each subcourse must be assigned at least one classroom at some time slot
model.forced_assignment = ConstraintList()
for c in C:
    for y in Y[c]:
        
        model.forced_assignment.add(sum(model.x[a, y, c, t] for a in A for t in T) == 1)

# ================= OBJECTIVE FUNCTION =================
model.obj = Objective(expr=
    sum(model.x[a, y, c, t] * get_distance(df_courses.loc[df_courses["COD"] == c, "Sede Dipartimento"].values[0],
                                           df_rooms.loc[df_rooms["Code"] == a, "Indirizzo"].values[0],
                                           distance_cache)
        for a in A for c in C for y in Y[c] for t in T),
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
    for (a, y, c, t) in model.x:
        if model.x[a, y, c, t].value > 0.5:  # If allocated

            # Compute the distance between the classroom and the department
            dept_location = df_courses.loc[df_courses["COD"] == c, "Sede Dipartimento"].values[0]
            classroom_location = df_rooms.loc[df_rooms["Code"] == a, "Indirizzo"].values[0]
            distance = get_distance(dept_location, classroom_location, distance_cache)


            allocation_results.append([y, a, t, s[a], n_y[c][y], distance, course_levels[c], cfu_y[c][y]])

    # Convert to DataFrame
    df_results = pd.DataFrame(allocation_results, columns=["Subclass Code", "Classroom ID", "Time Slot",
                                                        "Classroom Capacity", "Class Size", "Distance (km)", "Course Level", "CFU"])

    # Save to Excel
    with pd.ExcelWriter("Classroom_Allocation.xlsx") as writer:
        df_results.to_excel(writer, sheet_name="Allocation", index=False)

    print("✅ Results saved to 'Classroom_Allocation.xlsx'")

