from tfl_arrivals import db
from tfl_arrivals.models import *
from tfl_arrivals import db_uri, db_cache
import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from threading import Thread, Semaphore

def main():
    db.create_all()
    engine = create_engine(db_uri)
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)

    all_lines = db_cache.get_all_lines(session)
    # s = Semaphore(1)
    # counter = 0
    # for line in all_lines:
    #     print("=" * 20 + str(counter) + "=" * 50)
    #     s.acquire()
    #     t = Thread(target=db_cache.get_stops_of_line, args=(session, line.line_id))
    #     s.release()
    #     t.start()
    #     counter += 1
    counter = 0
    for line in all_lines:
        print("=" * 20 + str(counter) + "=" * 50)
        db_cache.get_stops_of_line(session, line.line_id)
        counter += 1



if __name__ == '__main__':
    main()
