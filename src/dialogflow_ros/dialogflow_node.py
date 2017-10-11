#!/usr/bin/env python
import rospy
import apiai

from std_msgs.msg import String

# Authentication
SESSION_ID = ''


class DialogflowNode(object):
    """
    ROS node for the Dialogflow natural language understanding.

    Dialogflow (previously API.ai) parses natural language into a json string containing the semantics of the text. This
    nose wraps that into a ROS actionlib interface.
    """
    def __init__(self):
        rospy.init_node('dialogflow_node')
        rospy.Subscriber("speech", String, self.speech_callback, queue_size=10)
        try:
            self._client_access_token = rospy.get_param("~client_access_token")
        except rospy.ROSException:
            rospy.logfatal("Missing required ROS parameter client_access_token")
            exit(1)

        self.ai = apiai.ApiAI(self._client_access_token)

        self.result_pub = rospy.Publisher("command", String, queue_size=10)
        self.request = None

    def speech_callback(self, msg):
        self.request = self.ai.text_request()
        self.request.query = msg.data

        rospy.logdebug("Waiting for response...")
        response = self.request.getresponse()
        rospy.logdebug("Got response, and publishing it.")

        result_msg = String()
        result_msg.data = response.read()

        self.result_pub.publish(result_msg)

if __name__ == "__main__":
    dialogflow_node = DialogflowNode()
    rospy.spin()
