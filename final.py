import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import tensorflow as tf
from keras.models import load_model
from tkinter import *
import tkinter.messagebox
import PIL.Image
import PIL.ImageTk
from tkinter import filedialog
from tkinter import filedialog
from flask import Flask, request, jsonify
import base64
from pymongo import MongoClient
import datetime
import bcrypt
import cv2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CATEGORIES=["Affected","Normal"]
model = tf.keras.models.load_model("CNN.model")

def get_database():
   CONNECTION_STRING = "mongodb+srv://srivarshan611:12345@cluster-1.gvgrwp3.mongodb.net/?retryWrites=true&w=majority"
   client = MongoClient(CONNECTION_STRING)
   return client['user_db']

dbname = get_database()
collection_name = dbname["users"]

@app.route("/signup", methods = ['POST'])
def signup():
    username = request.json["username"]
    password = request.json["password"]
    hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
    user = {
        "username" : username,
        "password" : hashed_password,
        "createdAt": datetime.datetime.now()
    }
    collection_name.insert_one(user)
    return "ok"

@app.route("/login", methods = ['POST'])
def login():
    username = request.json["username"]
    password = request.json["password"]
    hashed_password = password.encode('utf-8')
    db_pass = collection_name.find_one({"username": username})["password"]
    response = "response"
    if bcrypt.checkpw(hashed_password, db_pass):
        response = app.response_class(
            response="login successful",
            status=200,
            mimetype='application/json'
        )
    else:
        print("does not match")
        response = app.response_class(
            response="login failed",
            status=404,
            mimetype='application/json'
        )
    return response

def prepare(file):
    IMG_SIZE = 200
    img_array = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    #img_array = cv2.equalizeHist(img_array)

    #img_array = cv2.Canny(img_array, threshold1=3, threshold2=10)
    #img_array = cv2.medianBlur(img_array,1)
    new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    return new_array.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

count = 1

@app.route("/park", methods = ['POST'])
def detect():
    global count

    encoded_data = request.json['file']
    
    decoded_data = base64.b64decode((encoded_data))
    img_file = open('./images/image' + str(count) + '.jpeg', 'wb')
    img_file.write(decoded_data)
    img_file.close()
    count = count + 1

    prediction = model.predict(prepare(os.path.abspath(img_file.name)))
    prediction = list(prediction[0])
    print(prediction)
    return CATEGORIES[prediction.index(max(prediction))]
    
app.run()