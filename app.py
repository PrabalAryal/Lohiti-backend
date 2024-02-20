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


@app.route("/age", methods=["POST"])
def receive_age():
    age = request.json.get("age")
    return age


@app.route("/api/questions", methods=["GET"])
def get_questions():
    global correct_answers
    questions = collection_hard_questions.get_hard_questions()
    correct_answers = [question["correct_answer"] for question in questions]
    return jsonify(questions)

@app.route("/api/answers", methods=["POST"])
def receive_answers():
    age = receive_age()  
    answers = request.json.get("answers", [])
    score = 0
    print(correct_answers)
    print(answers)
    for i in range(min(len(answers), len(correct_answers))):
        if answers[i].lower() == correct_answers[i].lower():
            score += 1

    mean = 12  
    standard_deviation = 5.113
    z_score = (score - mean) / standard_deviation
    iq_score = (z_score * 15) + 100
    collection4.insert_one({"age": age, "score": score, "z_score": z_score})

    return jsonify({"score": iq_score})


# if __name__ == "__main__":
#     app.run(debug=True)
