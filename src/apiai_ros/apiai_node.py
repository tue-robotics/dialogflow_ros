#!/usr/bin/env python
"""ROS node for the API.ai natural language understanding"""


import rospy
import json
import apiai

from std_msgs.msg import Int16, String
from audio_common_msgs.msg import AudioData

# Authentication
CLIENT_ACCESS_TOKEN = 'fe9f5d6b687045d4a1531e389a25aa6e'
SESSION_ID = 'your_key'

# Audio configuration
CHANNELS = 1
RATE = 16000

# print resDict["result"]['resolvedQuery']
# return resDict["result"]['resolvedQuery']

class ApiaiNode():
    def __init__(self):
        rospy.init_node('apiai_node')

        rospy.Subscriber("trigger", Int16, self.trigger_callback, queue_size=1)

        self.resampler = apiai.Resampler(source_samplerate=RATE)
        # global CLIENT_ACCESS_TOKEN, SESSION_ID
        self.ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

        self.result_pub = rospy.Publisher("command", String, queue_size=10)


    def trigger_callback(self, msg):
        # todo(rokus): configure VAD if possible
        self.voice_activity_detector = apiai.VAD()
        self.request = self.ai.text_request()
        self.request.query = "Go to the kitchen"

        self.audio_sub = rospy.Subscriber("audio", AudioData, self.audio_callback)
        self.listening = True

        rospy.loginfo("Listening to audio...")

        try:
            r = rospy.Rate(10)
            while self.listening:
                r.sleep()
        except Exception as e:
            self.audio_sub.unregister()
            raise e
        except KeyboardInterrupt:
            self.audio_sub.unregister()

        rospy.loginfo("Got it!")

        rospy.loginfo("Waiting for response...")
        response = self.request.getresponse()
        rospy.loginfo("Got response, printing and publishing it!")

        print self.request._prepage_end_request_data()

        print response.read()

        result_msg = String()
        result_msg.data = response.read()

        self.result_pub.publish(result_msg)

    def audio_callback(self, msg):
        frames, data = self.resampler.resample(msg.data, len(msg.data)/2)

        if self.voice_activity_detector.processFrame(frames) != 1:
            self.listening = False
            self.audio_sub.unregister()
            rospy.loginfo("Stopped listening")
            return
        # self.request.send(data)

if __name__ == "__main__":
    apiai_node = ApiaiNode()

    rospy.spin(
)