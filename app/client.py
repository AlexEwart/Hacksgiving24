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
from pydantic import BaseModel
from playsound import playsound
import threading
from pydub import AudioSegment
import subprocess
import pygame
import re

import queue

class AudioPlayer:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.thread.start()

    def _audio_worker(self):
        while True:
            file_path = self.audio_queue.get()
            if file_path is None:
                break
            try:
                playsound(file_path)
            except Exception as e:
                print(f"Error playing audio: {e}")
            self.audio_queue.task_done()

    def play_audio(self, file_path):
        self.audio_queue.put(file_path)

    def stop(self):
        self.audio_queue.put(None)


# THIS SHOULD BE IN ENVIRONMENT FILE!!
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

MODEL="gpt-4o-mini"
class Client:
    def __init__(self):
        api_key = ""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", api_key))
        self.base_message = {
            "role": "system",
            "content": """
                You are a master museum tour guide. You are tasked with giving short and to-the-point answers to questions you are asked.
                
                Summarize the exhibit in responses tailored to the demographic of the individual. 
                Share fun facts about the exhibit, use the exhibit data to create your responses.
                Make sure you respond in the appropriate language so that it can be understood by the visitors. 
                Don't give long responses, and don't ask the users questions. Only talk about the exhibit and questions related to the exhibit. For example, if a user asks about the history leading up to the creation of the exhibit, tell them more.
             
                The "title" of your response should be the exhibit title, just translated into the desired language.
                
                Give your responses in the following JSON format, only including the curly braces and NOT the word json:
                
                {
                    "body": <string>
                }
            """
        }
        self.messages = [self.base_message]
        self.audio_lock = threading.Lock()
        self.is_playing = False

    def load_exhibit(self, prompt_data):
        self.messages.append({"role": "system", "content": json.dumps(prompt_data)})

    def get_age(self, img_path):
        base64_image = encode_image(img_path)
        self.messages.extend([
            {"role": "system", "content": """
                Looking at the image, identify the age of the person. Round up a little bit. Give your responses in the following JSON format, only including the curly braces and NOT the word json:
     
                {
                    "youngest_age": <number>
                }
            """},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"}
                }
            ]}
        ])
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            temperature=0.0,
        )
        self.messages.pop()
        return int(re.search(r'\d+', response.choices[0].message.content).group())

    def prompt_gpt(self, message_str):
        self.messages.append({"role": "user", "content": message_str})
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            temperature=0.0,
        )
        answer = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": answer})
        self.speak(answer)
        return answer

    def transcribe(self, audio_path):
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            if hasattr(transcription, 'text'):
                return transcription.text
            else:
                return None
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            return None

   
    def play_audio(self, file_path="output.mp3"):
        """
        Play the given audio file using pygame.
        """
        def audio_thread():
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                self.is_playing = True
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)  # Wait for the audio to finish
            except Exception as e:
                print(f"Error playing audio: {e}")
            finally:
                self.is_playing = False
                pygame.mixer.quit()

        thread = threading.Thread(target=audio_thread)
        thread.start()

    def stop_all_audio(self):
        """
        Stop all currently playing audio immediately using pygame.
        """
        try:
            if pygame.mixer.get_init():  # Check if pygame mixer is initialized
                pygame.mixer.music.stop()  # Stop the music if it's playing
                self.is_playing = False
        except Exception as e:
            print(f"Error stopping audio: {e}")
        finally:
            if pygame.mixer.get_init():
                pygame.mixer.quit()  # Quit the mixer only if it is initialized

    def is_audio_playing(self):
        """
        Check if audio is currently playing.
        """
        return self.is_playing

    def speak(self, transcript):
        """
        Generate speech from text and save it as an MP3 file, then play it.
        """
        try:
            with self.client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="alloy",
                input=transcript
            ) as response:
                response.stream_to_file("output.mp3")
        except Exception as e:
            print(f"Error during text-to-speech generation or playback: {e}")

    def reset(self):
        return Client()