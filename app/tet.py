





from flask import Flask, Response, render_template, jsonify, request
import cv2
import base64
from webcambackend import webcamBackend


temp_image_path = "captured_image.jpg"

analysis = DeepFace.analyze(
            img_path=temp_image_path,
            actions=['age', 'gender', 'race', 'emotion'],
            enforce_detection=False
        )

print(analysis)