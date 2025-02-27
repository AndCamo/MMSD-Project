import pandas as pd
import numpy as np
from pyomo.environ import *
from distance import get_distance, load_distance_dictionary


# ================= VARIABLE INDEX =================
ATTENDANCE_RATE = 0.2  # 60% of students attend classes
WEEKLY_HOURS = 40  # Hours available per classroom per week
MORNING_HOURS = 4 * 5  # Hours available in the morning
EVENING_HOURS = 4 * 5  # Hours available in the evening
SUBCOURSES_PER_COURSE = 3  # Number of subcourses per course
SUBCOURSE_CLASS_HOURS = 20  # Required classroom hours per subcourse per week
SUBCOURSE_LAB_HOURS = 0  # Required lab hours per subcourse per week

# ================= LOAD CLASSROOM DATA =================
df_rooms = pd.read_csv("MMSD-Project/Data/classroom_dataset.csv", sep=";")

A = df_rooms["Code"].tolist()  # List of all classrooms
L = df_rooms[df_rooms["aulaInformatica"] == 1]["Code"].tolist()  # List of computer labs
R = df_rooms[df_rooms["aulaInformatica"] == 0]["Code"].tolist()  # List of regular classrooms

s = dict(zip(df_rooms["Code"], df_rooms["Capienza"]))  # Classroom capacities
h = dict(zip(df_rooms["Code"], np.full(len(df_rooms), WEEKLY_HOURS)))  # Available hours per week

# ================= LOAD COURSE DATA =================
df_courses = pd.read_csv("MMSD-Project/Data/degree_dataset.csv", sep=";")

C = df_courses["COD"].tolist()  # List of courses
n = dict(zip(df_courses["COD"], df_courses["Participants"]))  # Number of students per course

# ================= LOAD DISTANCE DATA =================
distance_cache = load_distance_dictionary("MMSD-Project/Data/distance_dictionary.pkl")

# ================= CREATE SUBCOURSES AND STUDENT DISTRIBUTION =================
Y = {c: [f"{c}_Y{i+1}" for i in range(SUBCOURSES_PER_COURSE)] for c in C}  # Generate subcourses
subcourse_split = 1 / SUBCOURSES_PER_COURSE  # Even split (e.g., 50% each if 2 subcourses)
n_y = {c: {y: int(n[c] * subcourse_split) for y in Y[c]} for c in C}  # Students per subcourse

# ================= TIME SLOTS =================
T = ["M", "E"]
g = {"M": MORNING_HOURS, "E": EVENING_HOURS}

# ================= PYOMO MODEL =================
model = ConcreteModel()

# Decision Variables
model.x = Var([(a, y, c, t) for a in A for c in C for y in Y[c] for t in T], within=Binary)
#model.delta_u = Var([(y, c) for c in C for y in Y[c]], within=NonNegativeReals)
#model.delta_q = Var([(y, c) for c in C for y in Y[c]], within=NonNegativeReals)

# ================= CONSTRAINTS =================

# # Constraint: Ensure no room is double-booked at the same time
model.unique_assignment = ConstraintList()
for a in A:
    for t in T:
        model.unique_assignment.add(sum(model.x[a, y, c, t] for c in C for y in Y[c]) <= 1)

# # Constraint: Seat capacity must be sufficient for students attending the subcourse
model.seat_capacity = ConstraintList()
for c in C:
    for y in Y[c]:
        for a in A:
            for t in T:
                model.seat_capacity.add(model.x[a, y, c, t] * n_y[c][y] * ATTENDANCE_RATE <= s[a])

# # Constraint: Ensure required class and lab hours are met
model.hour_request = ConstraintList()
for c in C:
    for y in Y[c]:
        model.hour_request.add(sum(g[t] * model.x[a, y, c, t] for a in A for t in T) >= SUBCOURSE_CLASS_HOURS)
        #model.hour_request.add(sum(g[t] * model.x[a, y, c, t] for a in R for t in T) + model.delta_u[y, c] <= SUBCOURSE_CLASS_HOURS + 3)
        #model.hour_request.add(sum(g[t] * model.x[a, y, c, t] for a in L for t in T) + model.delta_q[y, c] >= SUBCOURSE_LAB_HOURS)
        #model.hour_request.add(sum(g[t] * model.x[a, y, c, t] for a in R for t in T) + model.delta_u[y, c] <= SUBCOURSE_LAB_HOURS + 3)

# Constraint: Each subcourse must be assigned at least one classroom at some time slot
# model.forced_assignment = ConstraintList()
# for c in C:
#     for y in Y[c]:
#         model.forced_assignment.add(sum(model.x[a, y, c, t] for a in A for t in T) >= 1)

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


            allocation_results.append([y, a, t, s[a], n_y[c][y], distance])  # Add distance to output

    # Convert to DataFrame
    df_results = pd.DataFrame(allocation_results, columns=["Subclass Code", "Classroom ID", "Time Slot",
                                                            "Classroom Capacity", "Class Size", "Distance (km)"])

    # Save to Excel
    with pd.ExcelWriter("Classroom_Allocation.xlsx") as writer:
        df_results.to_excel(writer, sheet_name="Allocation", index=False)

    print("✅ Results saved to 'Classroom_Allocation.xlsx'")

