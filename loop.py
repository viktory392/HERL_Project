# camera, vision model
import requests
import GPT4_vision
import Camera
import json

# GUI, language model
import tkinter as tk
from tkinter import simpledialog, messagebox
import openai
import GPT4
import ast
import math

# ROS
import rospy
import kinova_msgs.msg
from kinova_msgs.srv import *
import geometry_msgs.msg
import std_msgs.msg
from std_msgs.msg import String
import actionlib
import time
import Calculator
import Arm

# other
from typing import Dict, Tuple

# initialize arm
prefix = 'j2n6s300_'
arm = Arm.Arm(prefix)

# starting orientation calculated using functions in Calculator class
calc = Calculator.Calculator(items=None)
start_z_dist = 0.5
home_position = [0.221980864406, -0.257505953312, 0.508770644665]
home_euler = calc.to_rad([93.9, 63.8, 17.6])
home_quat = calc.EulerXYZ2Quaternion(home_euler)

# Set up key for models.
key = ''

def _get_models(key: str) -> Tuple[GPT4.GPT4, GPT4_vision.GPT4_vision]:
    """Gets the text and vision-text LLMs.
    Args:
      key: The OpenAI key to use for the models.
    Returns:
      A tuple of the text and vision-text LLMs.
    """
    client = openai.OpenAI(api_key=key)
    model1 = GPT4.GPT4(client)
    vision1 = GPT4_vision.GPT4_vision(client)
    return model1, vision1

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
    content = _postprocess_model_response(content)
    return json.loads(content)

def _get_text_prompt_preamble() -> str:
    """Returns the preamble for the prompt."""
    prompt_preamble = '''I will give you a sentence with the name of one 
    or more objects. Return a comma separated list of the names of the objects:
    the object names should be strings.'''
    return prompt_preamble

def _get_text_prompt(user_input: str) -> str:
    """Gets the prompt for the LLM."""
    prompt = _get_text_prompt_preamble() + '\n' + user_input
    return prompt

def homeArm():
    print('Homing JACO arm')
    rospy.wait_for_service('/j2n6s300_driver/in/home_arm')
    try:
        srvHome = rospy.ServiceProxy('j2n6s300_driver/in/home_arm', HomeArm)
        resp1 = srvHome()
        return resp1
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)

def move(linear, angular):
    '''Moves arm according to given coordinates and angles.'''
    cur_position = arm.get_currpose().position
    orientation = arm.get_currpose().orientation
    euler_orient = calc.Quaternion2EulerXYZ([orientation.x, orientation.y,
                                             orientation.z, orientation.w])
    deg_orient = calc.to_deg(euler_orient)
    target_position = [cur_position.x + linear[0], cur_position.y + linear[1],
                       cur_position.z + linear[2]]
    target_orient = calc.to_rad([deg_orient[0] + angular[0], deg_orient[1] + angular[1],
                                deg_orient[2] + angular[2]])
    qorient = calc.EulerXYZ2Quaternion(target_orient)
    arm.cartesian_pose_client(target_position, qorient)

def grip(f1,f2,f3):
    '''Moves fingers'''
    cur_finger_position = arm.getCurrentFingerPosition()
    target = [cur_finger_position.finger1 + f1, cur_finger_position.finger2 + f2,
              cur_finger_position.finger3 + f3]
    arm.gripper_client(target)

def check_vision_model_response(obj_distances) -> bool:
    """Checks the object distances.
    
    The object distances must obey Pythagoras theorem as a first
    approximation. Since the initial z-distance of the arm is known,
    the distance estimate must be greater than the initial z-distance.
    the distancec should also be positive.

    args:
      obj_distances: The dictionry of objects and estimated distances from
        the model.

    Retruns:
      True if the response meets the above criteria.
    """
    for obj in obj_distances.keys():
        if obj_distances[obj] <= 0:
            return False
        if obj_distances[obj] <= start_z_dist:
          return False
    
    return True

def talker():
    # Setup
    camera = Camera.Camera()
    model1, vision1 = _get_models(key=key)

    vision_prompt1 = f'''I will give you an image of a scene.
    The scene will contain some objects. Identify any objects
    in the image and estimate how far away they are in meters.
    The initial height from the camera to the objects is {start_z_dist} meters.
    Return a dictionary with each entry containing the name of
    the object (a single word) and its distance in meters,
    and nothing else.'''

    # capture image and get info about objects
    image = camera.get_image()
    obj_distances = _get_response_from_vision_model(
        vision1, vision_prompt1, image)
    print('Initial distances: ', obj_distances)

    vision_prompt_correction = f'''I will give you an image of a scene.
    The scene will contain some objects. Identify any objects
    in the image and estimate how far away they are in meters.
    The initial height from the camera to the objects is {start_z_dist} meters.

    In your previous estimate, you had returned these values:
    {obj_distances}.
    These estimates are not correct. Please re-estimate the
    distances.

    Return a JSON dictionary with each entry containing the name of
    the object (a single word) and its distance in meters,
    and nothing else.'''

    # if the vision model provides inaccurate distances, ask it to re-estimate
    if not check_vision_model_response(obj_distances):
        
        corrected_dist = _get_response_from_vision_model(
            vision1, vision_prompt_correction.format(start_z_dist, obj_distances), image)
        obj_distances = corrected_dist
        print('Corrected distances: ', obj_distances)

    # initialize ROS node
    rospy.init_node('talker', anonymous=True)
    homeArm()

    def get_objects(objects):
        '''Move to object, grab object, move back to start position.'''
        for obj in objects:
            print(obj)
            dist = obj_distances.get(obj)
            print(f"Estimated distance: {dist}")
            x_dist = math.sqrt(dist**2 - start_z_dist**2)
            # print(f"Distance to move: {x_dist}")
            move([0,0,0], [-268,-51,-71])
            move([x_dist,0,0], [0,0,0])
            move([0,0,-1*(start_z_dist)], [0,0,0])
            grip(3000,3000,3000)
            homeArm()
            grip(-3000,-3000,-3000)
    
    def execute():
        '''When go is pressed, execute the following commands.'''
        # get response from user input
        user_input = text_box.get("1.0", tk.END).strip()
        print(user_input)
        text_prompt = _get_text_prompt(user_input)
        response = model1.get_completion(text_prompt)
        obj_list = response.split(", ")
        print(obj_list)
        get_objects(obj_list)
    
    def exit_app():
        '''When exit is pressed, close the window.'''     
        root.destroy()

    # tkinter GUI
    root = tk.Tk()
    root.title('GUI')

    go_button = tk.Button(root, text='Go!', width=25, command=execute)
    go_button.pack(pady=10)

    exit_button = tk.Button(root, text='Exit', width=25, command=exit_app)
    exit_button.pack(pady=10)

    text_box = tk.Text(root, height=5, width=40)
    text_box.pack(pady=10)
    
    root.mainloop()

if __name__ == '__main__':
  try:
    talker()
  except rospy.ROSInterruptException():
    pass
