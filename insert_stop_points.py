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
    stop_file = open("stop_point_naptan_ids_all", "r")
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
                if stop.naptan_id not in ["490015502P", "490016293W", "490005198F",  "490005368N", "490000984X", "490000984Y"]:
                    assert(db_stop.name == stop.name)
                if stop.naptan_id not in ["940GZZLUBNK", "940GZZLUEUS", "940GZZLUICK", "490015114E", "490010100E", "940GZZCRKGH"]:
                    assert(db_stop.latitude == stop.latitude)
                    assert(db_stop.longitude == stop.longitude)

                if stop.sms_code != None and stop.sms_code != "" and \
                    db_stop.sms_code != stop.sms_code:
                    print(f"New sms code found for {stop.naptan_id}: {stop.sms_code}")
                    db_stop.sms_code = stop.sms_code
                db_stop.lines_bus = stop.lines_bus
                db_stop.lines_tube = stop.lines_tube
            else:
                session.add(stop)
            session.commit()

if __name__ == '__main__':
    main()
