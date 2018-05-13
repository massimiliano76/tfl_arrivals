from tfl_arrivals import db
from tfl_arrivals.models import *
from tfl_arrivals import db_uri, fetcher, config
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine


def generate_url(name, stop_letter):
    name = name.replace("   ", " ").\
        replace("  ", " ").\
        replace(" / ", " ").\
        replace("/", " ").\
        replace("&", "n").\
        replace("'", "").\
        replace(".", "").\
        replace(",", "").\
        replace("(", "").\
        replace(")", "").\
        replace("-", "_").\
        replace(" ", "_")

    if len(stop_letter) != 0 and "->" not in stop_letter:
        name = name + "_" + stop_letter

    return name.lower()

def main():
    config["app"]["cache_api_responses"] = "True"
    config["app"]["use_api_response_cache"] = "True"

    engine = create_engine(db_uri)
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)

    stops = session.query(StopPoint).all()

    used_urls = set()
    for stop in stops:
        url_base = generate_url(stop.name, stop.stop_letter)
        url = url_base
        counter = 0
        while url in used_urls:
            counter += 1
            url = f"{url_base}_{counter}"
        used_urls.add(url)
        stop.url = url

    session.commit()

if __name__ == '__main__':
    main()
