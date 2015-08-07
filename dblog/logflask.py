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

        @self.route('')
        def index():
            query = self._db.session.query(logdb.log_value)
            query = query.order_by(logdb.log_value.time.desc()).limit(100)
            query = query.from_self().join(logdb.log_tag)
            for key, value in request.args.iteritems():
                query = query.filter(logdb.log_tag.tag_key == key)
                query = query.filter(logdb.log_tag.tag_value == value)
            query = query
            output = ""
            for row in query.all():
                output += line(row) + "<BR>"
            return output

        @self.route('/insert', methods=['POST'])
        def insert():
            points = request.form["points"]
            db_points = [logdb.log_value.from_obj(obj) for obj in json.loads(points)]
            self._db.session.add_all(db_points)
            self._db.session.commit()
            return ""

        def line(row):
            import datetime
            time = datetime.datetime.fromtimestamp(
                int(row.time)
            ).strftime('%Y-%m-%d %H:%M:%S')
            return time + ": <a href='#' title='"+json.dumps(row.tags.dict())+"'>Tags</a> " + json.dumps(row.fields)