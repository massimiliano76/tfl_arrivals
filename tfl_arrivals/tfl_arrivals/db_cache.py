import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from tfl_arrivals import db_path, parser
from tfl_arrivals.arrival_data import Line, modes, LineId, StopId, StopPoint, CacheTimestamp, CachedDataType
from tfl_arrivals.fetcher import lines_fetcher, line_stops_fetcher, stop_fetcher
from datetime import datetime, timedelta
from typing import List, Callable

module_logger = logging.getLogger(__name__)

def __cache_lines(session, id: str):
    logger = logging.getLogger(__name__)
    for mode in modes:
        logger.info(f"Fetching mode {mode}")
        for line in  parser.parse_lines(lines_fetcher(mode)):
            logger.debug(f"Adding line {line.name} to database")
            session.add(line)

    session.commit()

def __delete_lines(session, id: str):
    session.query(Line).delete()
    session.commit()

def __get_update_timestamp(session, type: CachedDataType, id: str = None) -> datetime:
    logger = logging.getLogger(__name__)
    update_record_query = session.query(CacheTimestamp).\
        filter(CacheTimestamp.data_type == type)

    if id != None:
        update_record_query = update_record_query.filter(CacheTimestamp.data_id == id)

    update_record = update_record_query.order_by(CacheTimestamp.update_time.desc()).\
        limit(1).\
        one_or_none()
    if update_record == None:
        return None
    
    return update_record.update_time


def __save_update_timestamp(session, type: CachedDataType, id: str = None) -> None:
    ts = CacheTimestamp(data_type = type, data_id = id)
    session.add(ts)
    session.commit()

_DBUpdateFunc = Callable[[scoped_session, str], None]

class __UpdateDescription:
    def __init__(self, type: CachedDataType, id: str, valid_for: timedelta, update_func: _DBUpdateFunc, delete_func: _DBUpdateFunc):
#    def __init__(self, type: CachedDataType, id: str, valid_for: timedelta, update_func, delete_func):
        self.type = type
        self.id = id
        self.valid_for = valid_for
        self.update_func = update_func
        self.delete_func = delete_func

__line_list_update_description = __UpdateDescription(CachedDataType.line_list, "", timedelta(days=1), __cache_lines, __delete_lines)

def __update_cache(session, desc: __UpdateDescription):
    logger = logging.getLogger(__name__)
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    line_updated = __get_update_timestamp(session, desc.type)
    logger.debug(f"Cache for type {desc.type} last updated: {line_updated}")

    if line_updated == None or (datetime.utcnow() - line_updated) > desc.valid_for:
        logger.info(f"Refreshing {type} data")
        desc.delete_func(session, id)
        desc.update_func(session, id)
        __save_update_timestamp(session, desc.type)

def get_all_lines(session) -> List[Line]:
    __update_cache(session, __line_list_update_description)
    return session.query(Line).all()



def get_lines(session, line_id: LineId) -> List[Line]:
    logger = logging.getLogger(__name__)
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    line_updated = __get_update_timestamp(session, CachedDataType.line_list)
    logger.debug(f"Lines data last updated: {line_updated}")

    if line_updated == None or datetime.utcnow() - line_updated > timedelta(days=1):
        logger.info(f"Refreshing Lines data")
        session.query(Line).delete()
        __cache_lines(session)
        __save_update_timestamp(session, CachedDataType.line_list)

    return session.query(Line).filter(Line.line_id == line_id)


def __cache_line_stops(session, line_id: LineId):
    logger = logging.getLogger(__name__)
    #line = session.query(Line).filter(Line.line_id == line_id).one()
    line = get_line(session, line_id)

    logger.info(f"Fetching stops for line {line.line_id}")
    for stop in parser.parse_line_stops(line_stops_fetcher(line_id)):
        db_stop = session.query(StopPoint).filter(StopPoint.naptan_id == stop.naptan_id).one_or_none()
        if db_stop is not None:
            stop = db_stop
        stop.lines.append(line)
        logger.debug(f"Adding stop '{stop.name}', '{stop.indicator}' to database")        


def get_stops_of_line(line_id: LineId, session):
    logger = logging.getLogger(__name__)
    line_stops_updated = __get_update_timestamp(session, CachedDataType.line_stops, line_id)
    logger.debug(f"Lines stops last updated: {line_stops_updated}")

    if line_stops_updated == None or datetime.utcnow() - line_updated > timedelta(days=1):
        logger.info(f"Refreshing Line stops data for {line_id}")        
        __cache_line_stops(session, line_id)
        __save_update_timestamp(session, CachedDataType.line_stops)



    

def populate_stop(naptan_id: StopId):
    logger = logging.getLogger(__name__)
    session = _create_session()

    logger.info(f"Fetching stop {naptan_id}")

    stop = parser.parse_stop(stop_fetcher(naptan_id))        
    logger.debug(f"Adding stop '{stop.name}', '{stop.indicator}' to database")        
    session.add(stop)
    session.commit()

