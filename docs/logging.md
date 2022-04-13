You can log regular events or audit logs to additional log systems such as CloudWatch, Splunk,
Sumo Logic etc. 

All you need to do is add the necessary handlers to core.conf file on your local computer (rare) 
or on Cloud Node (common). 

## CloudWatch 

For CloudWatch, watchtower Python library is already installed on cloud node. 
You can update core.conf like the below to start logging.  

```
# 1- add CloudWatch handler key
[handlers]
keys = ... ,  cwHandler

# 2- Define handler, select level i.e. DEBUG, INFO and other parameters such as log format
[handler_cwHandler]
class = watchtower.CloudWatchLogHandler
level = DEBUG
formatter = simpleFormatter

# 3- Add the new handler to any logger  
[logger_practicus]
handlers = ... , cwHandler
```

For more information you can check [watchtower documentation](https://kislyuk.github.io/watchtower/) 

## Other log systems

For log systems other than CloudWatch, you need to install the necessary python logger libraries first.
And then you can add the log handler the same way as to CloudWatch
