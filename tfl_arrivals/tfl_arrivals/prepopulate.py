import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from tfl_arrivals import db_path, parser
from tfl_arrivals.arrival_data import Line, modes, LineId, StopId, StopPoint
from tfl_arrivals.fetcher import lines_fetcher, line_stops_fetcher, stop_fetcher

module_logger = logging.getLogger(__name__)

def _create_session():
    engine = create_engine(db_path)
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


def populate_line_stops(line: Line, session):
    logger = logging.getLogger(__name__)

    logger.info(f"Fetching stops for line {line.line_id}")
    for stop in parser.parse_line_stops(line_stops_fetcher(line.line_id)):
        db_stop = session.query(StopPoint).filter(StopPoint.naptan_id == stop.naptan_id).one_or_none()
        if db_stop is not None:
            stop = db_stop
        stop.lines.append(line)
        logger.debug(f"Adding stop '{stop.name}', '{stop.indicator}' to database")        

    

def populate_stop(naptan_id: StopId):
    logger = logging.getLogger(__name__)
    session = _create_session()

    logger.info(f"Fetching stop {naptan_id}")

    stop = parser.parse_stop(stop_fetcher(naptan_id))        
    logger.debug(f"Adding stop '{stop.name}', '{stop.indicator}' to database")        
    session.add(stop)
    session.commit()
