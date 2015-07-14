import json, datetime
from sqlalchemy import Column, ForeignKeyConstraint, Index, PrimaryKeyConstraint, text
from sqlalchemy.dialects.mysql import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator
from sqlalchemy import types
from sqlalchemy.orm import relationship, backref
from fakedict import CollectionDict

Base = declarative_base()
SCHEMA = 'log'

class json_type(TypeDecorator):
    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

    def copy(self):
        return json_type(self.impl.length)

def tag_value_setter(tag, value):
    tag.tag_value = value

class log_value(Base):
    __tablename__ = 'log_values'
    __table_args__ = {'schema': SCHEMA}

    id = Column(INTEGER, primary_key=True, nullable = False)
    measurement = Column(VARCHAR(64), nullable = False)
    fields = Column(json_type, nullable = False)
    time = Column(DOUBLE, nullable = False)
    _tags = relationship("log_tag", backref="log_value")

    @property
    def tags(self):
        if not hasattr(self, '_tag_dict'):
            self._tag_dict = CollectionDict(self._tags,
            col_key_getter = lambda item: item.tag_key,
            col_value_getter = lambda item: item.tag_value,
            col_value_setter = tag_value_setter,
            col_initializer = lambda name, value: log_tag(tag_key = name, tag_value = value))
        return self._tag_dict

    @staticmethod
    def from_obj(obj):
        measurement = obj["measurement"]
        fields = obj["fields"]
        tags = obj["tags"]
        value = log_value(measurement = measurement, fields = fields)
        if "time" in obj:
            value.time = obj["time"]
        for tag_key in tags:
            value.tags[tag_key] = tags[tag_key]
        return value

    def line(self):
        import datetime
        time = datetime.datetime.fromtimestamp(
            int(self.time)
        ).strftime('%Y-%m-%d %H:%M:%S')
        return time + ": " + str(self.fields)

    def __repr__(self):
        return "<log_value " + str(self.fields) + " " + str(self.tags) + " " + str(self.time) + " >"

Index('time_idx', log_value.time)
Index('measurement_idx', log_value.measurement)

class log_tag(Base):
    __tablename__ = 'log_tags'
    __table_args__ = {'schema': SCHEMA}

    log_id = Column(INTEGER, primary_key = True, nullable = False)
    tag_key = Column(VARCHAR(64), primary_key = True, nullable = False)
    tag_value = Column(VARCHAR(64), nullable = False)

    def __repr__(self):
        return "<log_tag " + str(self.tag_key) + ": " + str(self.tag_value) + ">"

Index('tag_key_val', log_tag.tag_key, log_tag.tag_value)
ForeignKeyConstraint(
        [log_tag.log_id], [log_value.id],
        use_alter=True, name='fk_element_parent_node_id'
    )
