# apiai_ros
ROS wrapper for API.ai

## Interfaces

### Subscribed topics
```
speech (std_msgs/String)
```
The transcribed speech to be interpreted by API.ai.
  
### Published topics
```
command (std_msgs/String)
```
The json string output from API.ai.

### Parameters
```
~client_access_token
```
The client access token for your API.ai agent is a required parameter. It can be found under agent settings on [API.ai](api.ai)
