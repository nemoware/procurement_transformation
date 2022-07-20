from peewee import PrimaryKeyField, CharField, TextField, ForeignKeyField

from db.entity.base_model import BaseModel


class Rate(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField(null=False, max_length=512, unique=True)  # 255


class Segment(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField(null=False, max_length=40, unique=True)


class Service(BaseModel):
    code = CharField(primary_key=True, max_length=18)
    # name = CharField(null=False, max_length=512, unique=True)  # 132
    name = TextField(null=False, unique=True)


class Stage(BaseModel):
    id = PrimaryKeyField(null=False)
    # name = CharField(null=False, max_length=255, unique=True)
    name = TextField(null=False, unique=True)


class Sub_segment(BaseModel):
    id = PrimaryKeyField(null=False)
    name = CharField(null=False, max_length=40, unique=True)


class Unit(BaseModel):
    id = CharField(primary_key=True, max_length=18)
    name = CharField(null=False, max_length=255, unique=True)


class Alternative_rate(BaseModel):
    name = CharField(primary_key=True, max_length=512)
    rate_id = ForeignKeyField(Rate)


class Unit_synonym(BaseModel):
    name = CharField(primary_key=True, max_length=512)
    unit_id = ForeignKeyField(Unit)
