from tfl_arrivals import db
from tfl_arrivals.models import *
from tfl_arrivals import db_uri, db_cache, fetcher, config
import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

def main():
    config["app"]["cache_api_responses"] = "True"
    config["app"]["use_api_response_cache"] = "True"

    engine = create_engine(db_uri)
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    db.create_all()
    stop_file = open("stop_point_naptan_ids2", "r")
    all_stops = [l.strip() for l in stop_file.readlines()]
    count = 0
    for file_naptan in all_stops:
        count += 1
        print(f"---------------- #{count} - {file_naptan}")
        for stop in fetcher.fetch_stops(file_naptan):
            print(f"---Inserting {stop.naptan_id}")
            db_stop = session.query(StopPoint).filter(StopPoint.naptan_id == stop.naptan_id).one_or_none()
            if db_stop is not None:
                assert(db_stop.naptan_id == stop.naptan_id)
                assert(db_stop.name == stop.name)
                assert(db_stop.latitude == stop.latitude)
                assert(db_stop.longitude == stop.longitude)
                if stop.sms_code != None and stop.sms_code != "" and \
                    db_stop.sms_code != stop.sms_code:
                    print(f"New sms code found for {stop.naptan_id}: {stop.sms_code}")
                    db_stop.sms_code = stop.sms_code
            else:
                session.add(stop)
            session.commit()

if __name__ == '__main__':
    main()
