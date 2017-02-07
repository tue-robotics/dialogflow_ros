#!/usr/bin/env python
"""ROS node for the API.ai natural language understanding"""

import rospy
import apiai
import collections
import requests
import json

from std_msgs.msg import String
from audio_common_msgs.msg import AudioData

from watson_speech_recognition import WatsonSpeech

# Authentication
CLIENT_ACCESS_TOKEN = 'fe9f5d6b687045d4a1531e389a25aa6e'
SESSION_ID = 'your_key'

WATSON_USERNAME = '59b2e9d6-9281-4471-a08c-3e3d3f55b72c'
WATSON_PASSWORD = 'EsUQ7VkG3YIi'

# Audio configuration
CHANNELS = 1
RATE = 16000

class SpeechRecognitionNode(object):
    def __init__(self):
        rospy.init_node('speech_recognition')

        # rospy.Subscriber("trigger", String, self.trigger_callback, queue_size=1)

        self.resampler = apiai.Resampler(source_samplerate=RATE)

        self.watson = WatsonSpeech(WATSON_USERNAME, WATSON_PASSWORD)

        self.result_pub = rospy.Publisher("command", String, queue_size=10)


    # def trigger_callback(self, msg):
        self.voice_activity_detector = apiai.VAD()

        self.audio_sub = rospy.Subscriber("audio", AudioData, self.audio_callback)
        self.listening = True
        self.watson.start()

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

        print response.text

        result_msg = String()
        result_msg.data = response.text

        self.result_pub.publish(result_msg)

    def audio_callback(self, msg):
        frames, data = self.resampler.resample(msg.data, len(msg.data)/2)

        self.watson.add_audio(data)

        if self.voice_activity_detector.processFrame(frames) != 1:
            self.listening = False
            self.audio_sub.unregister()
            self.watson.close()
            rospy.loginfo("Stopped listening")
            return

if __name__ == "__main__":
    speech_recognition_node = SpeechRecognitionNode()

    rospy.spin()
