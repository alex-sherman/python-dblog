#!/usr/bin/python
import dblog

service = dblog.LoggingService("/tmp/cache.db", db_uri = "http://localhost:5000/log", port = 9999, log_level = "debug")
service.run_wait()