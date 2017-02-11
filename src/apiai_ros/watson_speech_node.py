#!/usr/bin/env python

"""Needed:
sudo pip install ws4py
"""

from ws4py.client.threadedclient import WebSocketClient
import base64
import json
import ssl
import subprocess
import threading
import time
import rospy
from std_msgs.msg import String
from audio_common_msgs.msg import AudioData

"""
From the website:
{
  "url": "https://stream.watsonplatform.net/speech-to-text/api",
  "password": "",
  "username": ""
}
"""


class SpeechToTextClient(WebSocketClient):
    def __init__(self, recognized_callback, username, password):
        self.ws_url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
        auth_string = "%s:%s" % (username, password)
        self.base64string = base64.encodestring(auth_string).replace("\n", "")
        self.recognized_callback = recognized_callback
        self.listening = False
        self.buffer = ""

        try:
            WebSocketClient.__init__(self, self.ws_url,
                                     headers=[("Authorization",
                                               "Basic %s" % self.base64string)])
            self.connect()
        except:
            print "Failed to open WebSocket."

    def opened(self):
        self.send('{"action": "start", "content-type": "audio/l16;rate=16000", "inactivity_timeout":-1}')
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()

    def received_message(self, message):
        # print "type of message: " + str(type(message))
        message = json.loads(str(message))
        if "state" in message:
            if message["state"] == "listening" and not self.listening:
                self.listening = True
        elif "results" in message:
            self.recognized_callback(message["results"])
            # To keep listening we need to send an empty payload
            # http://www.ibm.com/watson/developercloud/doc/speech-to-text/websockets.shtml#WSstop
            # self.send(bytearray(''), binary=True)
        elif "error" in message:
            # We are currently asking for inactivity_timeout infinite
            # but
            # To keep it open we could send every... 25s this, instead:
            # self.send('{"action": "no-op"}')
            pass
        # print "Message received: " + str(message)

    def send_data(self, data):
        self.buffer += data

    def stream_audio(self):
        while not self.listening:
            time.sleep(0.1)

        while self.listening:
            try:
                if len(self.buffer) > 100:
                    self.send(bytearray(self.buffer), binary=True)
                    self.buffer = ""

            except ssl.SSLError as e:
                print "error: " + str(e)

    def close(self, *args):
        self.listening = False
        self.stream_audio_thread.join()
        WebSocketClient.close(self)


class WatsonSTTPub(object):
    def __init__(self):
        self.pub = rospy.Publisher('watson_stt', String, queue_size=1)
        rospy.Subscriber("trigger", String, self.trigger_cb, queue_size=1)

        self.username = rospy.get_param('~username')
        self.password = rospy.get_param('~password')

    def trigger_cb(self, msg):
        self.stt_client = SpeechToTextClient(self.recognized_cb, username=self.username, password=self.password)
        rospy.Subscriber("audio", AudioData, self.audio_cb, queue_size=100)

    def audio_cb(self, msg):
        self.stt_client.send_data(str(msg.data))

    def recognized_cb(self, results):
        # print results
        # [{u'alternatives': [{u'confidence': 0.982, u'transcript': u'hello '}], u'final': True}]
        if len(results) > 0 and len(results[0]["alternatives"]) > 0:
            sentence = results[0]["alternatives"][0]["transcript"]
            self.pub.publish(String(sentence))
            self.stt_client.close()

    def __del__(self):
        self.stt_client.close()


if __name__ == '__main__':
    rospy.init_node('watson_stt')
    wsttp = WatsonSTTPub()
    rospy.spin()