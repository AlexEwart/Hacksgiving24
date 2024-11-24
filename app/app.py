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
import threading

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
latest = "loading response"
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
    
    answer = client.prompt_gpt(prompt)
    return answer
    

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
    print(request.args.get("lang"))
    specific_exhibit = {
        "language": request.args.get("lang"),
        "age_of_viewer": AGE,
        "exhibit_title": title,
        "exhibit_description": data.loc[title][1],
        "exhibit_age_range": data.loc[title][2],
        "exhibit_topic_difficulty": data.loc[title][3],
        "exhibit_topics": data.loc[title][4],
        "exhibit_body": data.loc[title][8],
    }

    # Create a JSON for all exhibits with title and description
    all_exhibits = [
        {"exhibit_title": exhibit, "exhibit_description": row[1]} 
        for exhibit, row in data.iterrows()
    ]

    # Combine the data
    result = {
        "all_exhibits": all_exhibits,
        "specific_exhibit": specific_exhibit
    }
    print(result)
    client.load_exhibit(result)
    answer = talk("Tell me about the exhibit")
    global latest
    latest = answer
    
    return jsonify(answer), 200


@app.route("/toggle")
def toggle():
    print("TOGGLING")
    global client
    if client.is_audio_playing():
        client.stop_all_audio()
        status = "stopped"
    else:
        client.play_audio()
        status = "playing"
    return jsonify({"message": f"Audio is now {status}"}), 200





# Route to serve the video feed
@app.route("/video_feed")
def video_feed():
    return Response(
        webcam.get_video_feed(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/return")
def return_home():
    client = client.reset()
    
    return jsonify({"message": "Video feed stopped"})


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
    data = request.get_json()  # Get JSON data from the request
    recently_started = data.get("recentlyStarted", True)  # Default to True if not provided
    print("RECENTLY:")
    print(recently_started)

    success = audio.stop_recording(recently_started)

    # Handle the case where stopRecording was called within 0.5 seconds of startRecording
    if not recently_started:
        prompt = client.transcribe(AUDIO_PATH)
    else:
        return jsonify({"error": "could not stop"}), 200
    

    if prompt is None:
        prompt = "unintelligible"
        
    answer = talk(prompt)

    return jsonify(answer), 200


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
