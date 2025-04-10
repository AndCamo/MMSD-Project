# MMSD-Project [Classroom Assignment]

University project for the course “Modelli e Metodi per il Supporto alle Decisioni”. Master Degree in Computer Science, University of Turin, 2025

## 🚀 Project Overview

This project presents an optimization model for classroom assignment in a university. The goal is to assign classrooms to degree programs while minimizing the distance between the main building of each department and the assigned classrooms. Each program requires a specific number of hours per week and must accommodate a defined number of students.
## 📄 Formal Model

A detailed formalization of the optimization problem, including  parameters, variables, objective function, and constraints, is available in the following PDF document:

[📘 View the formal model](https://drive.google.com/file/d/1K0dqeROaieJtguNNR1Huhquuxb0Iq3lk/view?usp=sharing)


## 🛠️ Web App Installation Guide


The results obtained through the implemented model, are explorable in an agile and interactive way through a dedicated WebApp.
To install and run this application, follow the steps below:
1. **Clone the repository**  
    ```bash
      git clone https://github.com/AndCamo/MMSD-Project.git
      cd MMSD-Project 
    ```

2. **Set up a virtual environment** (optional but recommended)
   ```bash
      python -m venv venv
      source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

   
3. **Install dependencies**
      ```bash
      pip install -r requirements.txt
      ```
4. **Run the web application**

   The optimization model results can be explored via a web interface by running the `App/server.py` file.

5. **Access the app**

   Once the server is running, open your browser and go to:
   ```
   http://localhost:8080/
   ```


## 📁 Project Structure

```
MMSD-Project
├── App
│   ├── server.py
│   ├── static
│   │   ├── script
│   │   │   ├── data-script.js
│   │   │   └── map-script.js
│   │   └── style
│   │       ├── content-style.css
│   │       ├── main-style.css
│   │       ├── map-style.css
│   │       └── table-style.css
│   └── templates
│       └── homepage.html
├── Classroom_Allocation.xlsx
├── Data
│   ├── classroom_dataset.csv
│   ├── degree_dataset.csv
│   ├── distance_dictionary.pkl
│   ├── distanze.csv
│   ├── Elenco Aule - Clean.xlsx
│   ├── Elenco Aule - Usable.xlsx
│   ├── Elenco offerta Complete.xlsx
│   ├── Elenco_Lauree.csv
│   └── Raw Data
│       ├── Elenco Aule - Unito.it.xlsx
│       └── Elenco offerta 2024-2025.xlsx
├── data_cleaner.py
├── data_processing.py
├── distance_script.py
├── distance.py
├── model_test.py
├── model.py
├── README.md
├── Stats
│   ├── assignment_stats.csv
│   ├── degree_in_department.csv
│   └── usage.csv
└── test.py

10 directories, 29 files
```

Here's a breakdown of the key files and folders in the repository:

- `model.py` – Implements the optimization model used for classroom allocation.
- `Classroom_Allocation.xlsx` – Main output file of the model, containing the final classroom assignments for each degree.
- `APP/` – Contains all frontend and backend code related to the web application interface.
- `APP/server.py` – Runs the backend server for the web application.
- `data/` – Folder containing input data files.
- `data_processing.py` – Processes model output and computes summary statistics, which are saved in the `Stats/` directory.
- `requirements.txt` – Lists all Python dependencies required for running the project.

## 👥 Credits

Developed by:

- [**Andrea Camoia**](https://github.com/AndCamo)
- [**Manuel Ferreira**](https://github.com/manuel-rcferreira)
