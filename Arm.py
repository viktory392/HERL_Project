import roslib; roslib.load_manifest('kinova_demo'); roslib.load_manifest('mouth_mouse')
import rospy
import sys
import actionlib
import kinova_msgs.msg
import std_msgs.msg
import geometry_msgs.msg
import math
import argparse
import Calculator

class Arm:
    currposemsg = kinova_msgs.msg.KinovaPose()

    def __init__(self, prefix):
        self.prefix = prefix
    
    def get_currpose(self):
        topic_address = '/' + self.prefix + 'driver/out/tool_pose'
        currposemsg = rospy.wait_for_message(topic_address, geometry_msgs.msg.PoseStamped)
        return currposemsg.pose
    
    def getCurrentFingerPosition(self):
        # wait to get current position
        topic_address = '/' + self.prefix + 'driver/out/finger_position'
        finger_position = rospy.wait_for_message(topic_address, kinova_msgs.msg.FingerPosition)
        return finger_position

    def gripper_client(self, finger_positions):
        """Send a gripper goal to the action server."""
        action_address = '/' + self.prefix + 'driver/fingers_action/finger_positions'

        client = actionlib.SimpleActionClient(action_address,
                                            kinova_msgs.msg.SetFingersPositionAction)
        client.wait_for_server()

        goal = kinova_msgs.msg.SetFingersPositionGoal()
        goal.fingers.finger1 = float(finger_positions[0])
        goal.fingers.finger2 = float(finger_positions[1])
        # The MICO arm has only two fingers, but the same action definition is used
        if len(finger_positions) < 3:
            goal.fingers.finger3 = 0.0
        else:
            goal.fingers.finger3 = float(finger_positions[2])
        client.send_goal(goal)
        if client.wait_for_result(rospy.Duration(5.0)):
            return client.get_result()
        else:
            client.cancel_all_goals()
            rospy.logwarn('the gripper action timed-out')
            return None

    def cartesian_pose_client(self, position, orientation):
        """Send a cartesian goal to the action server."""
        action_address = '/' + self.prefix + 'driver/pose_action/tool_pose'
        client = actionlib.SimpleActionClient(action_address, kinova_msgs.msg.ArmPoseAction)
        client.wait_for_server()

        goal = kinova_msgs.msg.ArmPoseGoal()
        goal.pose.header = std_msgs.msg.Header(frame_id=(self.prefix + 'link_base'))
        goal.pose.pose.position = geometry_msgs.msg.Point(
            x=position[0], y=position[1], z=position[2])
        goal.pose.pose.orientation = geometry_msgs.msg.Quaternion(
            x=orientation[0], y=orientation[1], z=orientation[2], w=orientation[3])

        client.send_goal(goal)

        if client.wait_for_result(rospy.Duration(15.0)):
            return client.get_result()
        else:
            client.cancel_all_goals()
            print('the cartesian action timed-out')
            return None