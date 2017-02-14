#! /usr/bin/env python

import rospy
from std_msgs.msg import String
import subprocess
import os


def trigger_cb(msg):
    try:
        os.system("aplay ~/MEGA/sounds/ping.wav")
    except:
        rospy.logerr("aplay failed")

rospy.init_node("ping_player")
rospy.Subscriber("ping_trigger", String, trigger_cb, queue_size=10)
rospy.spin()