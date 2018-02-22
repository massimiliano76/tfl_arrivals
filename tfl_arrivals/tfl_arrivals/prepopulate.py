import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from tfl_arrivals import db_path, parser
from tfl_arrivals.arrival_data import Line, modes
from tfl_arrivals.fetcher import lines_fetcher

module_logger = logging.getLogger(__name__)

def populate_lines():
    logger = logging.getLogger(__name__)
    engine = create_engine(db_path)
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    for mode in modes:
        logger.info(f"Fetching mode {mode}")
        for line in  parser.parse_lines(lines_fetcher(mode)):
            logger.debug(f"Adding line {line.name} to database")
            session.add(line)

    session.commit()
