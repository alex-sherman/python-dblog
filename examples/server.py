#!/usr/bin/python
import dblog

service = dblog.LoggingService("/tmp/cache.db", 9999, log_level = "info")
service.run_wait()