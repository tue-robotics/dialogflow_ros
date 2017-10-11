# dialogflow_ros
ROS wrapper for Dialogflow (previously API.ai)

## Interfaces

### Subscribed topics
```
speech (std_msgs/String)
```
The transcribed speech to be interpreted by Dialogflow.

### Published topics
```
command (std_msgs/String)
```
The json string output from Dialogflow.

### Parameters
```
~client_access_token
```
The client access token for your Dialogflow agent is a required parameter. It can be found under agent settings on
[Dialogflow](https://dialogflow.com)
