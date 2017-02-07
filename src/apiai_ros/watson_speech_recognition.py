#!/usr/bin/env python

from ws4py.client.threadedclient import WebSocketClient
import base64, json, ssl, subprocess, threading, time

class WatsonSpeech(WebSocketClient):
    def __init__(self, username, password, rate=16000, bit_depth=16, endianness="l"):
        self.rate = rate
        self.bit_depth = bit_depth
        self.endianness = endianness

        self.ws_url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"

        auth_string = "%s:%s" % (username, password)
        self.base64string = base64.encodestring(auth_string).replace("\n", "")

        self.listening = False

    def start(self):
        try:
            WebSocketClient.__init__(self, self.ws_url,
                headers=[("Authorization", "Basic %s" % self.base64string)])
            self.connect()
            print "Opened WebSocket"
        except Exception as e:
            print e 
            print "Failed to open WebSocket."

        self.buffer = ""

    # def opened(self):
        self.send('{"action": "start", "content-type": "audio/' 
            + self.endianness + str(self.bit_depth) + ';rate=' + str(self.rate) + '"}')
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()
        print "Started audio stream"

    def received_message(self, message):
        message = json.loads(str(message))
        if "state" in message:
            if message["state"] == "listening":
                self.listening = True
        print "Message received: " + str(message)

    def add_audio(self, data):
        if not self.listening:
            return

        self.buffer + str(data)

    def stream_audio(self):
        while not self.listening:
            time.sleep(0.1)

        while self.listening:
            try: 
                self.send(bytearray(self.buffer), binary=True)
                self.buffer = ""
            except ssl.SSLError: pass

    def close(self):
        self.listening = False
        self.stream_audio_thread.join()
        WebSocketClient.close(self)