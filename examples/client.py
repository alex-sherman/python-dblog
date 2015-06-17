#!/usr/bin/python
import dblog

logger = dblog.LoggingClient()
logger.log("RSSI", -76, tags = {"card": "verizon"})
logger.log("stuff", fields = {"something": "what", "otherthing": "other"}, tags = {"card": "verizon"})
#logger.log("empty")
logger.info("Info")
logger.debug("Debug")
logger.warning("Warning")
logger.error("Error")