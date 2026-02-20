import base64
import requests

class GPT4_vision:
    def __init__(self, client):
        self.client = client
    
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
