#!/usr/bin/python
from flask import Flask
from dblog import LogBlueprint

app = Flask(__name__)

app.config["logger.db.uri"]='mysql://log@localhost'

app.register_blueprint(LogBlueprint)

if __name__ == '__main__':
    app.debug = True
    app.run()