#!/usr/bin/python
import dblog
import jrpc

proxy = jrpc.service.SocketProxy(9999, timeout = 5)
logger = dblog.Logger(proxy.log, tags = {"a thing": "a value"})
logger.log("RSSI", -76, tags = {"card": "verizon"})
logger.log("stuff", fields = {"something": "what", "otherthing": "other"}, tags = {"card": "verizon"})
#logger.log("empty")
logger.info("Info")
logger.debug("Debug")
logger.warning("Warning")
logger.error("Error")