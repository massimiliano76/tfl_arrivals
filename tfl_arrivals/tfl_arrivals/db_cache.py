import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from tfl_arrivals import db_path, parser
from tfl_arrivals.arrival_data import Line, modes, LineId, StopId, StopPoint, CacheTimestamp, CachedDataType
from tfl_arrivals.fetcher import lines_fetcher, line_stops_fetcher, stop_fetcher, line_data_fetcher
from datetime import datetime, timedelta
from typing import List, Callable

module_logger = logging.getLogger(__name__)

### All lines 
def __cache_lines(session: scoped_session, id: str) -> None:
    """Fetches the data for all lines from TFL ans stores in the database"""
    logger = logging.getLogger(__name__)
    for mode in modes:
        logger.info(f"Fetching mode {mode}")
        for line in  parser.parse_lines(lines_fetcher(mode)):
            logger.debug(f"Adding line {line.name} to database")
            session.add(line)

    session.commit()

def __delete_lines(session: scoped_session, id: str) -> None:
    """Deletes all line data from the database"""
    session.query(Line).delete()
    session.commit()


### Single line
def __cache_line_data(session: scoped_session, line_id: str) -> None:
    """Fetches the data for a single line from TFL ans stores in the database"""
    logger = logging.getLogger(__name__)
    line = parser.parse_line(line_data_fetcher(line_id))
    logger.debug(f"Adding line {line.name} to database")
    session.add(line)
    session.commit()

def __delete_line_data(session: scoped_session, id: str) -> None:
    """Deletes a single line data from the database"""
    session.query(Line).filter(Line.line_id == id).delete()
    session.commit()


### All stops for one line
def __cache_line_stops(session: scoped_session, line_id: LineId) -> None:
    """Fetches all stops data for a single line from TFL ans stores in the database"""
    logger = logging.getLogger(__name__)
    line = get_line(session, line_id)

    logger.info(f"Fetching stops for line {line.line_id}")
    for stop in parser.parse_line_stops(line_stops_fetcher(line_id)):
        db_stop = session.query(StopPoint).filter(StopPoint.naptan_id == stop.naptan_id).one_or_none()
        if db_stop is not None:
            stop = db_stop
        stop.lines.append(line)
        logger.debug(f"Adding stop '{stop.name}', '{stop.indicator}' to database")   
    session.commit()

def __delete_line_stops(session: scoped_session, line_id: LineId) -> None:
    """Deletes all stops data for a single line data from the database"""
    line = get_line(session, line_id)
    line.stops = []    
    session.commit()


def __get_update_timestamp(session: scoped_session, type: CachedDataType, id: str = None) -> datetime:
    """Gets a timestamp of the last update for a given CachedDataType and id pair.
    In the case of CachedDataType.line_list the id is not used"""    
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


def __save_update_timestamp(session: scoped_session, type: CachedDataType, id: str = "") -> None:
    """Stores the current time as the timestamp of the last update
   for a given CachedDataType and id pair"""
    ts = CacheTimestamp(data_type = type, data_id = id)
    session.add(ts)
    session.commit()

_DBUpdateFunc = Callable[[scoped_session, str], None]

class __UpdateDescription:
    """Encapsulates all the information needed to properly update one type of cached data"""
    def __init__(self, type: CachedDataType, id: str, valid_for: timedelta, update_func: _DBUpdateFunc, delete_func: _DBUpdateFunc):
        self.type = type
        self.id = id
        self.valid_for = valid_for
        self.update_func = update_func
        self.delete_func = delete_func

def __update_cache(session: scoped_session, desc: __UpdateDescription):
    """Using the information in the update description this function checks 
    when was the data stored in the database last updated.
    If the stored data is too old, it removes it from the database fetches 
    the current data, and stores it in the databse"""
    logger = logging.getLogger(__name__)
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    line_updated = __get_update_timestamp(session, desc.type, desc.id)
    logger.debug(f"Cache for type {desc.type} last updated: {line_updated}")

    if line_updated == None or (datetime.utcnow() - line_updated) > desc.valid_for:
        logger.info(f"Refreshing {type} data")
        desc.delete_func(session, desc.id)
        desc.update_func(session, desc.id)
        __save_update_timestamp(session, desc.type)

def get_all_lines(session: scoped_session) -> List[Line]:
    """Retrieves all lines, using the local database if possible"""
    ud = __UpdateDescription(CachedDataType.line_list, "", timedelta(days=1), 
                             __cache_lines, __delete_lines)
    __update_cache(session, ud)
    return session.query(Line).all()

def get_line(session: scoped_session, line_id) -> Line:
    """Retrieves one line, using the local database if possible"""
    ud = __UpdateDescription(CachedDataType.line_data, line_id, timedelta(days=1), 
                             __cache_line_data, __delete_line_data)
    __update_cache(session, ud)
    return session.query(Line).filter(Line.line_id == line_id).one()

def get_stops_of_line(session: scoped_session, line_id: LineId) -> List[StopPoint]:
    """Retrieves all the stops of one lines, using the local database if possible"""
    ud = __UpdateDescription(CachedDataType.line_stops, line_id, timedelta(days=1), 
                             __cache_line_stops, __delete_line_stops)
    __update_cache(session, ud)
    return session.query(StopPoint).filter(StopPoint.lines.any(line_id = line_id)).all()
   

#def populate_stop(naptan_id: StopId):
#    logger = logging.getLogger(__name__)
#    session = _create_session()

#    logger.info(f"Fetching stop {naptan_id}")

#    stop = parser.parse_stop(stop_fetcher(naptan_id))        
#    logger.debug(f"Adding stop '{stop.name}', '{stop.indicator}' to database")        
#    session.add(stop)
#    session.commit()

