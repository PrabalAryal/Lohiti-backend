from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import random

app = Flask(__name__)
CORS(app)
client = pymongo.MongoClient("mongodb+srv://lohiti:testdatabase@iq-question.zm5yyij.mongodb.net/")
db = client["iq_questions_db"]
collection = db["iq_questions"]
correct_answers = []


def get_all_questions():
    questions = list(collection.find({}, {"_id": 0}))
    return questions


def get_random_questions():
    questions = get_all_questions()
    random.shuffle(questions)
    return questions[:30]


@app.route("/", methods=["GET"])
def get_questions():
    questions = get_random_questions()
    return jsonify(questions)



@app.route('/api/answers', methods=['POST'])
def receive_answers():
    answers = request.get_json()
    # process the answers
    return jsonify({'message': 'Answers received'}), 200



