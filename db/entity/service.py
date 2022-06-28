from peewee import PrimaryKeyField, CharField, TextField

from db.entity.base_model import BaseModel


class Service(BaseModel):
    code = CharField(primary_key=True, column_name="OPR_USL_CODE", max_length=18)
    # name = CharField(null=False, column_name="USL_NAME", max_length=512, unique=True)  # 132
    name = TextField(null=False, column_name="USL_NAME", unique=True)
