#!/usr/bin/python
import dblog

service = dblog.LoggingService("/tmp/cache.db", port = 9999, log_level = "debug")
service.run_wait()