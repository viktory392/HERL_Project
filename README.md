This repository contains the code written by [Vikraanth Sinha](https://www.vikraanth.com) as a summer 2024 ASPIRE intern at [HERL](https://www.herl.pitt.edu)

The research project was focused on improving robotic-assisted manipulation for individuals with upper-limb impairments by integrating **Visual-Language Models (VLMs)** into the control loop.

### 1. Research Paper Summary

**Title:** *Visual-Language Model-Assisted Robot Manipulation for Users with Upper Limb Impairment*

**Core Objective:** The paper addresses the high "cognitive load" and complexity required for people with motor disabilities to control multi-Degree-of-Freedom (DoF) robotic arms (like a Jaco arm). Instead of requiring the user to control every joint or coordinate manually, the system uses a VLM to "understand" the scene and the user's intent.

**Key Technical Contributions:**

* **Shared Autonomy:** The system splits the work between the human and the AI. The human provides high-level commands (via voice or simple input), and the VLM handles the complex spatial reasoning (identifying objects and planning the grasp).
* **VLM Integration:** It utilizes the GPT-4 vision model to map natural language instructions (e.g., "Pick up the blue bottle") to specific pixel coordinates and object orientations in the robot's camera feed.
* **Reduced Complexity:** The system significantly lowers the time and effort required to complete activities of daily living (ADLs), such as drinking or moving objects, compared to traditional joystick-based control.

---

### 2. GitHub Repository: [viktory392/HERL](https://github.com/viktory392/HERL)

**Components:**

* **Robot Framework:** Based on **ROS (Robot Operating System)**, containing nodes for controlling the Kinova Jaco2 robotic arm.
* **Vision Module:** Implementation of the VLM-based object detection and grounding. This part processes camera frames to identify the "target" based on the user's language input.
* **UI/Interface:** Tools for the user to input commands, which are then translated into goals for the robot's motion planner.
* **Basic Unit Testing:** Basic Unit Tests for quarternion-to-Euler conversion and camera input processing.
