# camera, vision model
import openai
import requests
import GPT4_vision
import Camera
import json

# other
from typing import Dict, Tuple

# Set up key for model.
key = 'sk-proj-Ksxqe0dz46vcPGc2Md5HT3BlbkFJtSoLEZjNInsUEPUZh9QV'

start_z_dist = 0.61

def _get_model(key: str) -> GPT4_vision.GPT4_vision:
    """Gets the text and vision-text LLMs.
    Args:
      key: The OpenAI key to use for the models.
    Returns:
      A tuple of the text and vision-text LLMs.
    """
    client = openai.OpenAI(api_key=key)
    vision1 = GPT4_vision.GPT4_vision(client)
    return vision1

def _get_headers(key: str) -> Dict[str, str]:
    """Gets the headers for the model."""
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {key}"
    }
    return headers

def _get_vision_model_payload(
        vision_model: GPT4_vision.GPT4_vision, vision_prompt: str,
        image_file_name: str) -> str:
    """Gets payload for vision model."""
    encoded_image = vision_model.encode_image(image_file_name)
    payload = {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": vision_prompt
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image}",
                "detail": "high"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }
    return payload

def _postprocess_model_response(content: str) -> str:
    """Postprocesses the model response to remove any JSON headers and quotes."""
    start = content.find('{')
    end = content.find('}')
    if start == -1:
        raise ValueError(f'model response {content} did not contain an opening curly bracket.')
    elif end == -1:
        raise ValueError(f'model response {content} did not contain an closing curly bracket.')
    else:
        content = content[start:end+1]
    return content

def _get_response_from_vision_model(
        vision_model: GPT4_vision.GPT4_vision, vision_prompt: str,
        image_file_name: str) -> dict:
    """Gets the response from the vision model."""
    payload = _get_vision_model_payload(vision_model, vision_prompt, image_file_name)
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=_get_headers(key),
        json=payload)
    result = response.json()
    content = result['choices'][0]['message']['content']
    print('model response: ', content)
    content = _postprocess_model_response(content)
    print('model response after: ', content)
    return json.loads(content)

def check_vision_model_response(obj_distances) -> bool:
    """Checks the object distances.
    
    The object distances must obey Pythagoras theorem as a first
    approximation. Since the initial z-distance of the arm is known,
    the distance estimate must be greater than the initial z-distance.
    the distance should also be positive.

    args:
      obj_distances: The dictionry of objects and estimated distances from
        the model.

    Retruns;
      True if the response meets the above criteria.
    """
    for obj in obj_distances.keys():
        if obj_distances[obj] <= 0:
            return False
        if obj_distances[obj] <= start_z_dist:
          return False
    
    return True

def main():
    # Setup
    camera = Camera.Camera()
    vision1 = _get_model(key=key)

    vision_prompt1 = f'''I will give you an image of a scene.
    The scene will contain some objects. Identify any objects
    in the image and estimate how far away they are in meters.
    The initial height from the camera to the objects is {start_z_dist} meters.
    Return a dictionary with each entry containing the name of
    the object (a single word) and its distance in meters,
    and nothing else.'''

    # capture image and get info about objects
    image = camera.get_image()
    image = '/Users/vikraanthsinha/Desktop/HERL/paper materials/pictures/IMG_1970.jpg'
    obj_distances = _get_response_from_vision_model(
        vision1, vision_prompt1, image)
    print('Initial distances: ', obj_distances)

    # vision_prompt_correction = f'''I will give you an image of a scene.
    # The scene will contain some objects. Identify any objects
    # in the image and estimate how far away they are in meters.
    # The initial height from the camera to the objects is {start_z_dist} meters.

    # In your previous estimate, you had returned these values:
    # {obj_distances}.
    # These estimates are not correct. Please re-estimate the
    # distances.

    # Return a JSON dictionary with each entry containing the name of
    # the object (a single word) and its distance in meters,
    # and nothing else. Return the dictionary as plain text.'''

    # if not check_vision_model_response(obj_distances):
        
    #     corrected_dist = _get_response_from_vision_model(
    #         vision1, vision_prompt_correction.format(start_z_dist, obj_distances), image)
    #     obj_distances = corrected_dist
    #     print('Corrected distances: ', obj_distances)

if __name__ == '__main__':
    main()
