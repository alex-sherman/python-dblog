#!/usr/bin/python
import dblog

service = dblog.LoggingService(9999, log_level = "info")
service.run_wait()