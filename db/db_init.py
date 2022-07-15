import logging

import peewee

from db.config import db_handle
from db.entity.historical_lot import HistoricalLot
from db.entity.lot import Lot
from db.entity.simple_entity import *

logger = logging.getLogger(__name__)


def create_table() -> bool:
    try:
        db_handle.connect()
        Unit.create_table(safe=True)
        Sub_segment.create_table(safe=True)
        Stage.create_table(safe=True)
        Service.create_table(safe=True)
        Segment.create_table(safe=True)
        Rate.create_table(safe=True)
        Lot.create_table(safe=True)
        HistoricalLot.create_table()
        Alternative_rate.create_table(safe=True)
        Unit_synonym.create_table(safe=True)
        return True
    except peewee.InternalError as px:
        logger.exception(px)
        return False
