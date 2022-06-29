from db.entity.simple_entity import *


class Lot(BaseModel):
    procurement_id = PrimaryKeyField(null=False, column_name="PROCUREMENT_ID")
    segment_id = ForeignKeyField(Segment)
    sub_segment_id = ForeignKeyField(Sub_segment)
    service_code = ForeignKeyField(Service)
    stage_id = ForeignKeyField(Stage)
    rate_id = ForeignKeyField(Rate)
    unit_id = ForeignKeyField(Unit)
