import jrpc
import inspect
import datetime
import influxdb

LOG_LEVELS = ["info", "debug", "warning", "error"]

class LoggingService(jrpc.service.SocketObject):
    def __init__(self, port = 9999, log_level = "warning"):
        self.log_level = LOG_LEVELS.index(log_level)
        jrpc.service.SocketObject.__init__(self, port, debug = False)
        self.influxdb = influxdb.InfluxDBClient('influxdb.wirover.com', 8086, 'root', 'root', 'example')

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

        point = {"measurement": name, "fields": fields, "tags": tags, "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
        print point
        self.influxdb.write_points([point])

class LoggingClient(jrpc.service.SocketProxy):
    def __init__(self, port = 9999, timeout = 5):
        jrpc.service.SocketProxy.__init__(self, port, timeout = timeout)

    def _msg(self, msg, level, back):
        f = inspect.currentframe()
        for i in range(back):
            f = f.f_back
        mod = f.f_code.co_filename
        lineno = f.f_lineno
        date = datetime.datetime.now()
        self.log("log", fields = {"value": str(msg), "filename": mod, "line": lineno}, log_level = level)

    def info(self, msg, back = 2):
        self._msg(msg, "info", back)
    def debug(self, msg, back = 2):
        self._msg(msg, "debug", back)
    def warning(self, msg, back = 2):
        self._msg(msg, "warning", back)
    def error(self, msg, back = 2):
        self._msg(msg, "error", back)
