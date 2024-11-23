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

data = pd.DataFrame()
def read_data():
    data = pd.read_excel('../data.xlsx', index_col=0, header=None)
    return data

data = read_data()

# THIS SHOULD BE IN ENVIRONMENT FILE!!
api_key = ""
# API KEY IN HERE!!

## Set the API key and model name
MODEL="gpt-4o-mini"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", api_key))

# Open the image file and encode it as a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

IMAGE_PATH = "family.png"

def prompt_gpt(img_path, prompt_data):
    
    base64_image = encode_image(img_path)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": """
                You are a master museum tour guide. You are tasked with giving age and language appropriate descriptions for the exhibits in the museum.
                
                You will be given multiple pieces of information from the user:
                language: your responses should be in this language.
                exhibit_title: the official title of the exhibit.
                exhibit_description: brief information about the exhibit
                exhibit_body: More extensive info about how the exhibit works, etc.
                Image: an image containing museum visitors.
            
                Your task is to summarize the exhibit information in a way that the visitors can understand.
                When you look at the image, find the youngest person in that image and tailor your response to fit their age.
                Make sure you respond in the appropriate language so that it can be understood by the visitors.

                Give your responses in the following JSON format, only including the curly braces and NOT the word json:
             
                {
                    "youngest_age": <number>
                    "info_title": <string>
                    "info_body": <string>
                }
            """},
            {"role": "user", "content": json.dumps(prompt_data)},
            {"role": "user", "content": [
                # {"type": "text", "text": "What's the area of the triangle?"},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ],
        temperature=0.0,
    )
    # data = json.loads() # this should be the response we want
    return response.choices[0].message.content;

# Initialize Flask app and webcam backend
app = Flask(__name__)
webcam = webcamBackend()
data = pd.DataFrame()

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Route to serve the video feed
@app.route("/video_feed")
def video_feed():
    return Response(
        webcam.get_video_feed(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/gpt_prompt")
def test_lang():
    title = request.args.get("title")
    # this should be changed to access the database
    prompt_data = {
    "language": request.args.get("lang"),
    "exhibit_title": title,
    "exhibit_description": data.loc[title][1],
    "exhibit_body": data.loc[title][8]
    }

    res = prompt_gpt(IMAGE_PATH, prompt_data)
    return jsonify(res), 200

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

# @app.route("/initialize", methods=["POST"])
# def start_feed():
#     success = webcam.start_webcam()
#     return jsonify(
#         {"message": "Video feed started" if success else "Failed to start video feed"}
#     )



# @app.route("/capture_image", methods=["POST"])
# def capture_image():
#     frame = webcam.capture_frame()
#     if frame is None:
#         return jsonify({"error": "Failed to capture image"}), 500

#     temp_image_path = "captured_image.jpg"
#     cv2.imwrite(temp_image_path, frame)

#     try:
#         # Analyze the image
#         analysis = DeepFace.analyze(
#             img_path=temp_image_path,
#             actions=['age', 'gender', 'race', 'emotion'],
#             enforce_detection=False
#         )

#         # Extract and simplify the analysis
#         simplified_analysis = {
#             "age": analysis[0]['age'],
#             "race": analysis[0]['dominant_race'],
#             "gender": analysis[0]['dominant_gender'],
#             "emotion": analysis[0]['dominant_emotion']
#         }

#         return jsonify({
#             "message": "Image captured and analyzed successfully",
#             "analysis": simplified_analysis
#         }), 200

#     except ValueError as e:
#         return jsonify({"error": f"No face detected: {str(e)}"}), 400
#     except Exception as e:
#         return jsonify({"error": f"DeepFace analysis failed: {str(e)}"}), 500

# Homepage route
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

# %%
