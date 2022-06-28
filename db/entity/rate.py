from peewee import PrimaryKeyField, CharField

from db.entity.base_model import BaseModel


class Rate(BaseModel):
    id = PrimaryKeyField(null=False, column_name="OPR_USL_UNIT_ID")
    name = CharField(null=False, column_name="OPR_USL_UNIT", max_length=512, unique=True)  # 255
