from peewee import BooleanField, IntegerField, CompositeKey, Model

from db.config import db_handle
from db.entity.simple_entity import *


class Lot(Model):
    procurement_id = CharField(null=False)
    segment_id = ForeignKeyField(Segment)
    sub_segment_id = ForeignKeyField(Sub_segment)
    service_code = ForeignKeyField(Service)
    stage_id = ForeignKeyField(Stage)
    rate_id = ForeignKeyField(Rate)
    unit_id = ForeignKeyField(Unit)
    is_null = BooleanField(null=True)
    is_from_excel = BooleanField(null=True)

    class Meta:
        database = db_handle
        primary_key = CompositeKey('procurement_id',
                                   'segment_id',
                                   'sub_segment_id',
                                   'service_code',
                                   'stage_id',
                                   'rate_id',
                                   'unit_id')
