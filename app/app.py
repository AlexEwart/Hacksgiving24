from flask import Flask, Response, render_template, jsonify, request
import cv2
import base64
from webcambackend import webcamBackend
import numpy as np
import pandas as pd
import openai

# Initialize Flask app and webcam backend
app = Flask(__name__)
webcam = webcamBackend()
data = pd.DataFrame()

# %%
def read_data():
    data = pd.read_excel('../data.xlsx', index_col=0, header=None)
    return data

# %%
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

# @app.route("/initialize", methods=["POST"])
# def start_feed():
#     success = webcam.start_webcam()
#     return jsonify(
#         {"message": "Video feed started" if success else "Failed to start video feed"}
#     )



@app.route("/capture_image", methods=["POST"])
def capture_image():
    frame = webcam.capture_frame()
    if frame is None:
        return jsonify({"error": "Failed to capture image"}), 500

    temp_image_path = "captured_image.jpg"
    cv2.imwrite(temp_image_path, frame)

    try:
        # Analyze the image
        analysis = DeepFace.analyze(
            img_path=temp_image_path,
            actions=['age', 'gender', 'race', 'emotion'],
            enforce_detection=False
        )

        # Extract and simplify the analysis
        simplified_analysis = {
            "age": analysis[0]['age'],
            "race": analysis[0]['dominant_race'],
            "gender": analysis[0]['dominant_gender'],
            "emotion": analysis[0]['dominant_emotion']
        }

        return jsonify({
            "message": "Image captured and analyzed successfully",
            "analysis": simplified_analysis
        }), 200

    except ValueError as e:
        return jsonify({"error": f"No face detected: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"DeepFace analysis failed: {str(e)}"}), 500

# Homepage route
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

# %%
