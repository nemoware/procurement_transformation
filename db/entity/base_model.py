from peewee import *

from db.config import db_handle


class BaseModel(Model):
    class Meta:
        database = db_handle
