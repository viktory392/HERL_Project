# title Imports

import io
import os
import numpy as np
import pandas as pd
import PIL.Image
from IPython import display
import google.generativeai as genai
from google.colab import auth

auth.authenticate_user()
api_key = 'AIzaSyDirdojy8pxeC69XtPiMh_WKwzwK0kh0PU'
genai.configure(api_key=api_key)

pro_model = genai.GenerativeModel('gemini-pro-vision')
img_file = '12_Messy Kitchen.jpg'
with open(img_file, 'rb') as f:
  img = PIL.Image.open(f)
  display.display(img.resize((300, 200)))

text_prompt = 'Describe in detail everything that you see in this image.'
content = [img, text_prompt]

response = pro_model.generate_content(
    content,
    generation_config=genai.types.GenerationConfig(
      # Only 1 candidate for now
      candidate_count=1,
      stop_sequences=['x'],
      max_output_tokens=250,
      temperature=0.5,
    ),
    stream=True,
)
response.resolve()
print(response.text)

