from peewee import CharField, DateField, BlobField

from db.entity.base_model import BaseModel


class HistoricalLot(BaseModel):
    konkurs_id = CharField()
    ofr_id = CharField()
    lot_name = CharField(max_length=1024)
    usl_code = CharField()
    usl_name = CharField()
    purchase_date = DateField()
    embedding = BlobField()

