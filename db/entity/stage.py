from peewee import PrimaryKeyField, CharField, TextField

from db.entity.base_model import BaseModel


class Stage(BaseModel):
    id = PrimaryKeyField(null=False, column_name="OPR_USL_STAGE_ID")
    # name = CharField(null=False, column_name="OPR_USL_STAGE", max_length=255, unique=True)
    name = TextField(null=False, column_name="OPR_USL_STAGE", unique=True)
