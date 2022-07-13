from peewee import *

from db.config import db_handle


class HistoricalLot(Model):
    konkurs_id = CharField()
    ofr_id = CharField()
    lot_name = CharField(max_length=1024)
    usl_code = CharField()
    usl_name = CharField()
    purchase_date = DateField(null=True)
    embedding = BlobField()

    class Meta:
        database = db_handle
        primary_key = CompositeKey('konkurs_id', 'ofr_id')
        table_name = 'historical_lots'



