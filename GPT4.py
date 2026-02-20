import openai
import ast
import os

class GPT4:
    def __init__(self, client):
        self.client = client
    
    def get_completion(self, prompt, model="gpt-3.5-turbo"):
        """Takes in prompt and returns completion."""
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0)
        return response.choices[0].message.content
