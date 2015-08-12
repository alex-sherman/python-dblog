# DBlog
DBlog is a Python logging library, giving systems the capabability to log data directly to a database in a simple way.
This project was started after we attempted to use InfluxDB and found it too buggy/complicated and difficult to work with.
DBlog is very similar in functionality to InfluxDB, it's API is rather similar but all the components are very small and contained.


Architecture
---
The DBlog system is composed of three main parts

- The database server storing the logs
- A LoggingService running on a client of the server
- The Logger, a Python object responsible capable of logging data

From the bottom up, an application wishing to log data will instantiate a Logger object, and point it at a running LoggingService on the local machine.
Then the client can log data like so:

```python
proxy = jrpc.service.SocketProxy(9999, timeout = 5)
logger = dblog.Logger(proxy.log)
logger.info("Thermometer service started")
logger.log("Temperature", 45, tags = {"season": "fall"})
```

The Logger object calls on the LoggingService which is responsible for knowing the current log level of the system, and storing any log lines that meet the log level criteria to the database server.
It's also responsible for caching and ensuring that the log lines actually do make it to the database even in the event of power failure or network outage.

Once the data has been stored to the database, it can be queried against in MySQL directly to generate reports.
Alternatively, if the log lines were generated with .info, .warning, etc. an included Flask blueprint can be used to see recent human readable log lines.
