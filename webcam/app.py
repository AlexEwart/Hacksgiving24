from flask import Flask, Response, render_template, jsonify
import cv2
from webcambackend import webcamBackend

# Initialize Flask app and webcam backend
app = Flask(__name__)
webcam = webcamBackend()


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


# Homepage route
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
