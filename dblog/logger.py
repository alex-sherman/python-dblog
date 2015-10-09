import jrpc, json
import inspect
import datetime
import time
from postcache import POSTCache

LOG_LEVELS = ["debug", "info", "warning", "error"]

class LoggingService(jrpc.service.SocketObject):
    def __init__(self, cache_path, db_uri = None, port = 9999, log_level = "warning", offload_interval = 5):
        jrpc.service.SocketObject.__init__(self, port, debug = False)
        self.set_log_level(log_level)
        self.logger = Logger(self.log)
        if db_uri != None:
            db_uri += '/insert'
        self.cache = POSTCache(db_uri, cache_path, async_interval=10, data_key="points", check_same_thread=False)

    def console_log(self, name, value = None, fields = None, log_level = "info", tags = None):
        if LOG_LEVELS.index(log_level) < self.log_level:
            return
        filename = fields['filename'].split("/")[-1].split("\\")[-1]
        return str(datetime.datetime.now()) + " " + log_level + " " + filename + ":" + str(fields['line']) + " - " + fields['value']

    @jrpc.service.method
    def set_log_level(self, log_level):
        self.log_level = LOG_LEVELS.index(log_level)

    @jrpc.service.method
    def log(self, name, value = None, fields = None, log_level = "info", tags = None):
        if LOG_LEVELS.index(log_level) < self.log_level:
            return
        if fields == None:
            if value == None:
                raise ValueError("Value and fields cannot be None")
            fields = {"value": value}
        elif value != None:
            raise ValueError("Value and fields cannot both have a value")

        if tags == None:
            tags = {}
        tags["log_level"] = log_level

        point = {"measurement": name, "fields": fields, "tags": tags, "time": int(time.time())}
        self.cache.add_request(json.dumps(point))
        if name == "log":
            return self.console_log(name, value, fields, log_level, tags)
        return None

    def close(self):
        jrpc.service.SocketObject.close(self)
        self.logger.warning("Logging service exiting")

class Logger:
    def __init__(self, log_callback, tags = None):
        self._log = log_callback
        self.tags = tags

    def log(self, name, value = None, fields = None, log_level = "info", tags = None):
        if self._log == None: return
        if tags == None: tags = {}
        if self.tags != None: tags.update(self.tags)
        try:
            return self._log(name, value, fields, log_level, tags)
        except Exception as e:
            return str(e)

    def _msg(self, msg, level, back, tags):
        f = inspect.currentframe()
        for i in range(back):
            f = f.f_back
        mod = f.f_code.co_filename
        lineno = f.f_lineno
        date = datetime.datetime.now()
        output = self.log("log", fields = {"value": str(msg), "filename": mod, "line": lineno}, log_level = level, tags = tags)
        if output != None:
            print output

    def info(self, msg, back = 2, tags = None):
        self._msg(msg, "info", back, tags)
    def debug(self, msg, back = 2, tags = None):
        self._msg(msg, "debug", back, tags)
    def warning(self, msg, back = 2, tags = None):
        self._msg(msg, "warning", back, tags)
    def error(self, msg, back = 2, tags = None):
        self._msg(msg, "error", back, tags)
