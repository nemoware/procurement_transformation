from peewee import PrimaryKeyField, CharField

from db.entity.base_model import BaseModel


class Sub_segment(BaseModel):
    id = PrimaryKeyField(null=False, column_name="OPR_USL_SUBSEG_ID")
    name = CharField(null=False, column_name="OPR_USL_SUBSEGMENT", max_length=40, unique=True)
