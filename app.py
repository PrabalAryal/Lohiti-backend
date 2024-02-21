from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import random
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor


app = Flask(__name__)
CORS(app)
client = pymongo.MongoClient(
    "mongodb+srv://lohiti:testdatabase@iq-question.zm5yyij.mongodb.net/"
)
db = client["iq_questions_db"]
db2 = client["iq_questions_db"]
db3 = client["iq_questions_db"]
db4 = client["iq_questions_db"]
collection = db["iq_questions"]
collection2 = db2["iq_questions_medium"]
collection3 = db3["iq_questions_hard"]
collection4 = db4["results"]
correct_answers = []
age = 0


class collection_easy_questions:
    @staticmethod
    def get_easy_questions():
        easy_question = list(collection.find({}, {"_id": 0}))
        random.shuffle(easy_question)
        return easy_question[:6]


class collection_medium_questions:
    @staticmethod
    def get_medium_questions():
        medium_question = list(collection2.find({}, {"_id": 0}))
        random.shuffle(medium_question)
        return medium_question[:6]


class collection_hard_questions(collection_easy_questions, collection_medium_questions):
    @staticmethod
    def get_hard_questions():
        easy_question1 = collection_easy_questions.get_easy_questions()
        medium_question1 = collection_medium_questions.get_medium_questions()
        hard_question = list(collection3.find({}, {"_id": 0}))
        random.shuffle(hard_question)
        questions = list(easy_question1 + medium_question1 + hard_question[:8])
        random.shuffle(questions)
        return questions


@app.route("/api/questions", methods=["GET"])
def get_questions():
    global correct_answers
    questions = collection_hard_questions.get_hard_questions()
    correct_answers = [question["correct_answer"] for question in questions]
    return jsonify(questions)


@app.route("/api/answers", methods=["POST", "GET"])
def receive_answers():
    # age = receive_age()  # Assuming this function is defined elsewhere
    answers = request.json.get("answers", [])
    time_taken = request.json.get("time_taken", 0)  # Get time taken
    score = 0
    print(correct_answers)
    print(answers)
    for i in range(min(len(answers), len(correct_answers))):
        if answers[i].lower() == correct_answers[i].lower():
            score += 1
    data = pd.DataFrame(list(collection4.find()))
    x = data[["score", "time"]]
    y = data["iq_score"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )
    model = GradientBoostingRegressor()
    model.fit(x_train, y_train)
    z_score = (score - np.mean(data["score"])) / np.std(data["score"])
    iq_score = model.predict([[score, time_taken]])
    collection4.insert_one(
        {
            "score": score,
            "z_score": z_score,
            "iq_score": iq_score[0],
            "time": time_taken,
        }
    )
    return jsonify({"score": iq_score[0]})


@app.route("/api/score", methods=["GET"])
def get_latest_score():
    item = collection4.find().sort([("_id", pymongo.DESCENDING)]).limit(1)
    score = int(item[0]["iq_score"])
    return jsonify({"score": score})


# if __name__ == "__main__":
#   app.run(debug=True)
