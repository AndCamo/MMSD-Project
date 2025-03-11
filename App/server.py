from flask import Flask, render_template
import pandas as pd
import  json

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/get_dataset')
def get_data():
    classroom_dataset = pd.read_csv("../Data/classroom_dataset.csv", sep=";")
    degree_dataset = pd.read_csv("../Data/degree_dataset.csv", sep=";")
    result_dataset = pd.read_excel("../Classroom_Allocation.xlsx")
    response_data = {
        "classroom_dataset": classroom_dataset.to_json(orient="records"),
        "degree_dataset": degree_dataset.to_json(orient="records"),
        "result_dataset": result_dataset.to_json(orient="records")
    }

    return json.dumps(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
