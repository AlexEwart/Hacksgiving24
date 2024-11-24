from flask import Flask, Response, render_template, jsonify, request
import cv2
import base64
from webcambackend import webcamBackend
import numpy as np

from openai import OpenAI 
import os
from IPython.display import Image, display, Audio, Markdown
import base64
import json
import pandas as pd
from audiobackend import audioBackend
from client import Client


data = pd.DataFrame()
def read_data():
    data = pd.read_excel('../data.xlsx', index_col=0, header=None)
    return data

data = read_data()
audio = audioBackend()
client = Client()
# THIS SHOULD BE IN ENVIRONMENT FILE!!

## Set the API key and model name
MODEL="gpt-4o-mini"
AGE = 2
# Open the image file and encode it as a base64 string

IMAGE_PATH = "captured_image.jpg"
AUDIO_PATH = "recording.wav"


# Initialize Flask app and webcam backend
app = Flask(__name__)
webcam = webcamBackend()






def get_age():
    global AGE
    print("getting age")
    AGE = client.get_age(IMAGE_PATH)
    print(AGE)

def talk(prompt):
    return client.prompt_gpt(prompt)
    

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route("/gpt_prompt")
def test_lang():
    title = request.args.get("title")
    # this should be changed to access the database
    prompt_data = {
    "language: ": request.args.get("lang"),
    "age of viewer: ": AGE,
    "exhibit_title: ": title,
    "exhibit_description: ": data.loc[title][1],
    "exhibit_age-range: ": data.loc[title][2],
    "exhibit_topic-difficulty: ": data.loc[title][3],
    "exhibit_topics: ": data.loc[title][4],
    "exhibit_body: ": data.loc[title][8],
    }
    print(prompt_data)
    client.load_exhibit(prompt_data)

    return jsonify(talk("Tell me about the exhibit")), 200


# Route to serve the video feed
@app.route("/video_feed")
def video_feed():
    return Response(
        webcam.get_video_feed(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/stop_feed", methods=["POST"])
def stop_feed():
    webcam.stop_webcam()
    return jsonify({"message": "Video feed stopped"})


@app.route("/start_feed", methods=["POST"])
def start_feed():
    success = webcam.start_webcam()
    return jsonify(
        {"message": "Video feed started" if success else "Failed to start video feed"}
    )



@app.route("/capture_image", methods=["POST"])
def capture_image():
    frame = webcam.capture_frame()
    if frame is None:
        return jsonify({"error": "Failed to capture image"}), 500
    
    cv2.imwrite(IMAGE_PATH, frame)
    get_age()
    return jsonify({"message": "got image"})

# Homepage route

@app.route("/start_recording", methods=["POST"])
def start_recording():
    success = audio.start_recording()
    if success:
        return jsonify({"message": "Audio recording started"}), 200
    else:
        return jsonify({"error": "Audio is already recording"}), 400

@app.route("/stop_recording", methods=["POST"])
def stop_recording():
    success = audio.stop_recording()
    prompt = client.transcribe(AUDIO_PATH)
    return jsonify(talk(prompt)), 200

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

# %%
