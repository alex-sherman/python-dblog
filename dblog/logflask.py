# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
import json
import datetime, time
import orm as logdb

class LogBlueprint(Blueprint):
    def __init__(self, *args, **kwargs):
        try:
            self._db = kwargs.pop('db')
        except KeyError:
            raise KeyError("Missing argument: db")
        super(LogBlueprint, self).__init__(*args, **kwargs)

        @self.route('/')
        def index():
            return str(self._db.session.query(logdb.log_value).all())
