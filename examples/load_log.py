#!/usr/bin/python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dblog.orm

def load(user = "root", engine = None):
    if engine == None:
        engine = create_engine('mysql://{0}@localhost'.format(user))
    dblog.orm.Base.metadata.create_all(engine)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: load_log.py <user>"
        exit()
    load(sys.argv[1])
