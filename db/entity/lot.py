from peewee import PrimaryKeyField, ForeignKeyField

from db.entity.base_model import BaseModel
from db.entity.rate import Rate
from db.entity.segment import Segment
from db.entity.service import Service
from db.entity.stage import Stage
from db.entity.sub_segment import Sub_segment
from db.entity.unit import Unit


class Lot(BaseModel):
    procurement_id = PrimaryKeyField(null=False, column_name="PROCUREMENT_ID")
    segment_id = ForeignKeyField(Segment)
    sub_segment_id = ForeignKeyField(Sub_segment)
    service_code = ForeignKeyField(Service)
    stage_id = ForeignKeyField(Stage)
    rate_id = ForeignKeyField(Rate)
    unit_id = ForeignKeyField(Unit)
