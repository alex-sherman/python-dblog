# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, current_app
import json
import datetime, time
import orm as logdb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import aliased

mod = Blueprint('logger', __name__, url_prefix='/log')
DB_URI = "mysql://log@localhost/log"

@mod.record
def record(state):
    db = state.app.config.get("logger.db")

    if db is None:
        db_uri = state.app.config.get("logger.db.uri")
        if db_uri==None:
            db_uri=DB_URI
        engine = create_engine(db_uri)
        state.app.config["logger.db"] = sessionmaker(bind = engine)

    

@mod.route('')
def index():
    session = current_app.config["logger.db"]()
    session.query(logdb.log_value)

    for key, value in request.args.iteritems():
        tag_alias = aliased(logdb.log_tag)
        query = query.join(tag_alias)
        query = query.filter(tag_alias.tag_key == key)
        query = query.filter(tag_alias.tag_value == value)

    query = query.filter(logdb.log_value.measurement == "log")
    query = query.order_by(logdb.log_value.time.desc()).limit(100)

    output = ""
    for row in query.all():
        output += line(row) + "<BR>"
    session.close()
    return output

@mod.route('/insert', methods=['POST'])
def insert():
    rdata = request.get_json()
    points = rdata["points"]
    db_points = [logdb.log_value.from_obj(obj) for obj in points]
    session = current_app.config["logger.db"]()
    session.add_all(db_points)
    session.commit()
    session.close()
    return ""

def line(row):
    import datetime
    time = datetime.datetime.fromtimestamp(
        int(row.time)
    ).strftime('%Y-%m-%d %H:%M:%S')
    return str(row.id) + " " + time + ": <a href='#' title='"+json.dumps(row.tags.dict())+"'>Tags</a> <b>Line: " +\
        str(row.fields["line"]) + "</b> <i>" + str(row.fields["filename"]) + "</i> " + str(row.fields["value"])