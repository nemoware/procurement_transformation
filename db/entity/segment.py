from peewee import PrimaryKeyField, CharField

from db.entity.base_model import BaseModel


class Segment(BaseModel):
    id = PrimaryKeyField(null=False, column_name="OPR_USL_SEGMENT_ID")
    name = CharField(null=False, column_name="OPR_USL_SEGMENT", max_length=40, unique=True)
