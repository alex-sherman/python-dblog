#!/usr/bin/python
import dblog

service = dblog.LoggingService("/tmp/cache.db", 9999, log_level = "debug")
service.run_wait()