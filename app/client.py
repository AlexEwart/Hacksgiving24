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

import re



# THIS SHOULD BE IN ENVIRONMENT FILE!!
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
# API KEY IN HERE!!
class Age(BaseModel):
    age: int
    reasoning: str

MODEL="gpt-4o-mini"
class Client:
    def __init__(self):
        api_key = ""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", api_key))
        self.messages=[
                {"role": "system", "content": """
                    You are a master museum tour guide. You are tasked with giving short and to-the-point answers to questions you are asked.
                    
                    Summarize the exhibit in responses tailored to the demographic of the individual. 
                    Share fun facts about the exhibit, use the exhibit data to create your responses.
                    Make sure you respond in the appropriate language so that it can be understood by the visitors. 
                    Don't give long responses, and don't ask the users questions. Only talk about the exhibit and questions related to the exhibit. For example, if a user asks about the history leading up to the creation of the exhibit, tell them more.
                    Occasionally advise your audience to look at the signs around the exhibit.
                 
                    The "title" of your response should be the exhibit title, just translated into the desired language.
                    
                    Give your responses in the following JSON format, only including the curly braces and NOT the word json:
                    
                    {
                        "title": <string>
                        "body": <string>
                    }
                """}
        ]
        
    def load_exhibit(self, prompt_data):
        self.messages.append({"role": "system", "content": json.dumps(prompt_data)})
    
    
    def get_age(self, img_path):
        base64_image = encode_image(img_path)
        self.messages.extend([{"role": "system", "content": """
                               Looking at the image, identify the age of the person. Round up a little bit. Give your responses in the following JSON format, only including the curly braces and NOT the word json:
             
                                {
                                    "youngest_age": <number>
                                }
                               
                               """},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"}
                    }
                ]}])
        
        
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            temperature=0.0,
        )
        self.messages.pop()
         # data = json.loads() # this should be the response we want
        return int(re.search(r'\d+', response.choices[0].message.content).group())
            
    def prompt_gpt(self, message_str):
        self.messages.append({"role": "user", "content": message_str})
        
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            temperature=0.0,
        )
        print("GPT SAYS:")
        answer = response.choices[0].message.content
        print(answer)
        self.messages.append({"role": "assistant", "content": answer})
        return response.choices[0].message.content
    
    def transcribe(self, audio_path):
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Check if the transcription contains text
            if hasattr(transcription, 'text'):
                print(transcription.text)
                return transcription.text
            else:
                print("No transcription text available.")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        
            

        