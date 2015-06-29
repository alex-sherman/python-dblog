import jrpc, json
import inspect
import datetime
import influxdb
import sqlite3
import threading, time

LOG_LEVELS = ["debug", "info", "warning", "error"]

class LoggingOffload(threading.Thread):
    def __init__(self, logger, cache_path, interval, db_credentials = ('influxdb.wirover.com', 8086, 'root', 'root', 'example')):
        threading.Thread.__init__(self)
        self.logger = logger
        self.cache_path = cache_path
        self.interval = interval
        self.running = True
        self.influxdb = influxdb.InfluxDBClient(*db_credentials, timeout = 10)

    def run(self):
        self.logger.info("Logging service offloader started")
        conn = sqlite3.connect(self.cache_path)
        c = conn.cursor()
        while self.running:
            c.execute("select ROWID, point from logcache")
            rows = c.fetchall()
            if(len(rows) > 0):
                max_row_id = max([row[0] for row in rows])
                points = [json.loads(row[1]) for row in rows]
                try:
                    self.influxdb.write_points(points)
                    c.execute("delete from logcache where ROWID <= ?", [max_row_id])
                    conn.commit()
                    self.logger.debug("Wrote "+str(len(points))+" rows to influxdb")
                except Exception as e:
                    self.logger.debug(e)
            # A more responsive sleep, this terminates within 100 ms when the service
            # unsets running
            for i in range(self.interval * 10):
                if not self.running: return
                time.sleep(.1)

class LoggingService(jrpc.service.SocketObject):
    def __init__(self, cache_path, port = 9999, log_level = "warning", offload_interval = 10):
        self.log_level = LOG_LEVELS.index(log_level)
        jrpc.service.SocketObject.__init__(self, port, debug = False)
        self.cache_path = cache_path
        self.cache_conn = sqlite3.connect(cache_path, check_same_thread=False)
        self.cache_c = self.cache_conn.cursor()
        self.cache_c.execute("CREATE TABLE if not exists logcache (point text)")
        self.logger = Logger(self.log)
        self.offload = LoggingOffload(self.logger, cache_path, offload_interval)
        self.offload.start()

    def console_log(self, name, value = None, fields = None, log_level = "info", tags = None):
        if LOG_LEVELS.index(log_level) < self.log_level:
            return
        filename = fields['filename'].split("/")[-1].split("\\")[-1]
        return str(datetime.datetime.now()) + " " + log_level + " " + filename + ":" + str(fields['line']) + " - " + fields['value']

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
        self.cache_c.execute("INSERT into logcache VALUES (?)", [json.dumps(point)])
        self.cache_conn.commit()
        if name == "log":
            return self.console_log(name, value, fields, log_level, tags)
        return None

    def close(self):
        jrpc.service.SocketObject.close(self)
        self.logger.warning("Logging service exiting")
        if self.offload != None:
            self.offload.running = False

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
