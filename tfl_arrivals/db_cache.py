import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, exc
from tfl_arrivals.models import modes, StopId, StopPoint, CacheTimestamp, CachedDataType, Arrival, ArrivalRequest
from tfl_arrivals.fetcher import fetch_stops, fetch_arrivals
from datetime import datetime, timedelta
from typing import List, Callable

module_logger = logging.getLogger(__name__)

### Single Stop Point
def __cache_stop_point(session: scoped_session, naptan_id: str) -> None:
    """Fetches the data for a single stop point from TFL and stores in the database"""
    logger = logging.getLogger(__name__)
    stops = fetch_stops(naptan_id)
    for stop in stops:
        #logger.debug(f"Adding stop '{stop.name}', '{stop.indicator}' to database")
        # TODO This should do a proper update instead of remove-instert
        session.query(StopPoint).filter(StopPoint.naptan_id == stop.naptan_id).delete()
        __save_update_timestamp(session, CachedDataType.stop_point, stop.naptan_id)
        session.add(stop)
    session.commit()

# TODO Separate delete and update step doesn't work for stops as a singe
# fetch usually returns multiple stops, not just the one requested
# For now __delete_stop_point has been merged to __cache_stop_point
def __delete_stop_point(session: scoped_session, id: str) -> None:
    """Deletes a single line data from the database"""
    # session.query(StopPoint).filter(StopPoint.naptan_id == id).delete()
    # session.commit()


### Arrivals at a single stop point
def __cache_arrivals(session: scoped_session, naptan_id: str) -> None:
    """Fetches the arrivals for a single stop point from TFL and stores in the database"""
    logger = logging.getLogger(__name__)
    arrivals = fetch_arrivals(naptan_id)
    logger.info(f"Adding arrivals for '{naptan_id}' to database")
    for arrival in arrivals:
        db_arrival = session.query(Arrival).filter(Arrival.arrival_id == arrival.arrival_id).one_or_none()
        if db_arrival is not None:
            db_arrival.update_with(arrival)
        else:
            session.add(arrival)
    session.commit()

def __delete_arrivals(session: scoped_session, id: str) -> None:
    """Deletes a arrivals for a single stop point from the database"""
    session.query(Arrival).filter(Arrival.naptan_id == id).delete()
    session.commit()


### Cache update timestamp helpers
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
    ts = session.query(CacheTimestamp).filter(CacheTimestamp.data_type == type).filter(CacheTimestamp.data_id == id).one_or_none()
    if ts == None:
        session.add(CacheTimestamp(data_type = type, data_id = id))
    else:
        ts.update_time = datetime.utcnow();
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
    last_updated = __get_update_timestamp(session, desc.type, desc.id)
    logger.debug(f"Cache for type {desc.type}, {desc.id} last updated: {last_updated}")

    if last_updated == None or (datetime.utcnow() - last_updated) > desc.valid_for:
        logger.info(f"Refreshing {desc.type} data, id = '{desc.id}'")
        desc.delete_func(session, desc.id)
        desc.update_func(session, desc.id)
        __save_update_timestamp(session, desc.type, desc.id)



### Public methods

def search_stop(session: scoped_session, query_string: str, max_count: int) -> List[StopPoint]:
    """Retrieves all the stops from the local database that matches the query. If
    more than max_count matches are in the database, an empty list is returned"""

    q = session.query(StopPoint).filter(StopPoint.name.like(f"%{query_string}%")).\
        order_by(StopPoint.mode_tube.desc(),
            StopPoint.mode_dlr.desc(),
            StopPoint.mode_overground.desc(),
            StopPoint.mode_tram.desc(),
            StopPoint.name)

    if q.count() > max_count:
        return []
    else:
        return q.all()


def get_stop_point(session: scoped_session, naptan_id: StopId) -> StopPoint:
    # ud = __UpdateDescription(CachedDataType.stop_point, naptan_id, timedelta(days=1),
    #                          __cache_stop_point, __delete_stop_point)
    # __update_cache(session, ud)
    return session.query(StopPoint).filter(StopPoint.naptan_id == naptan_id).one_or_none()

def get_stop_point_by_url(session: scoped_session, url: str) -> StopPoint:
    return session.query(StopPoint).filter(StopPoint.url == url).one_or_none()

def __refresh_arrivals(session: scoped_session, naptan_id: StopId) -> List[Arrival]:
    ud = __UpdateDescription(CachedDataType.arrival, naptan_id, timedelta(minutes=1),
                             __cache_arrivals, __delete_arrivals)
    __update_cache(session, ud)
    session.commit()



def get_arrivals(session: scoped_session, naptan_id: StopId) -> List[Arrival]:
    try:
        __refresh_arrivals(session, naptan_id)
    except exc.DataError as e:
        logger(f"Cannot refresh arrival info for {naptan_id}:", e)
        return []

    req = session.query(ArrivalRequest).filter(ArrivalRequest.naptan_id == naptan_id).one_or_none()
    if req == None:
        session.add(ArrivalRequest(naptan_id=naptan_id))
    else:
        req.request_time = datetime.utcnow()
    session.commit()

    return session.query(Arrival).\
        filter(Arrival.naptan_id == naptan_id).\
        filter(Arrival.ttl > datetime.utcnow()).\
        order_by(Arrival.expected).\
        limit(6).all()

def refresh_recently_requested_stop_ids(session: scoped_session) -> List[StopId]:
    logger = logging.getLogger(__name__)
    tracking_time_limit = timedelta(minutes=15)
    session.query(ArrivalRequest).\
        filter(ArrivalRequest.request_time < (datetime.utcnow() - tracking_time_limit)).\
        delete()
    session.commit()
    recent_queries = session.query(ArrivalRequest).order_by(ArrivalRequest.naptan_id).all()
    if len(recent_queries) == 0:
        logger.info(f"No arrivals were requested in the last {tracking_time_limit.seconds/60} minutes")
    for q in recent_queries:
        try:
            __refresh_arrivals(session, StopId(q.naptan_id))
        except exc.DataError as e:
            logger(f"Cannot refresh arrival info for {q.naptan_id}:", e)
