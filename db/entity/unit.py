from peewee import PrimaryKeyField, CharField

from db.entity.base_model import BaseModel


class Unit(BaseModel):
    id = PrimaryKeyField(null=False, column_name="OPR_USL_UNIT_ID")
    name = CharField(null=False, column_name="USL_QUAN_UNIT", max_length=255, unique=True)
