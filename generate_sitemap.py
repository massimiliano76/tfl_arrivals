from tfl_arrivals import db
from tfl_arrivals.models import *
from tfl_arrivals import db_uri, fetcher, config
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
import math

def dist(poi, stop):
    dla = abs(poi[0] - stop.latitude)
    dlo = abs(poi[1] - stop.longitude)
    return math.sqrt(dlo*dlo + dla*dla)

def main():
    config["app"]["cache_api_responses"] = "True"
    config["app"]["use_api_response_cache"] = "True"

    engine = create_engine(db_uri)
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)

    stops = session.query(StopPoint).all()

    pois = [[51.530054, -0.124049], # King's Cross
            [51.505054, -0.217969], # Shepherd's Bush
            [51.503631, -0.112224], # Waterloo
            [51.564487, -0.104812], # Finsbury Park
            [51.481413, -0.010082], # Cutty Sark
            [51.501012, -0.126085], # Westminster
            [51.463387, -0.168883], # Clapham Juncton
            [51.460971, -0.139188], # Clapham common
            [51.524701, -0.034602], # Mile End
            [51.504606, -0.019777], # Canary Wharf
            [51.525881, -0.087674], # Old Street
            [51.492826, -0.223858], # Hammersmith
            [51.495723, -0.143429], # Victoria
            [51.509467, -0.076610], # Tower of London
            [51.494676, -0.174573], # South Kensington
            ]


    f = open("sitemap.xml", "w")
    current_date = "2018-05-13"
    f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
   <url>
      <loc>http://www.arrivalsoflondon.co.uk/</loc>
      <lastmod>{current_date}</lastmod>
      <changefreq>weekly</changefreq>
      <priority>0.8</priority>
   </url>""")
    added_urls = set()
    for stop in stops:
        add = True
        # add = False
        if stop.url in added_urls:
            continue
        # if stop.mode_dlr or stop.mode_tram or stop.mode_tube:
        #     add = True
        # else:
        #     for poi in pois:
        #         if dist(poi, stop) < 0.004:
        #             add  = True
        #             break

        if add:
            print(stop.naptan_id, stop.name, stop.stop_letter)
            added_urls.add(stop.url)
            f.write(f"""
   <url>
      <loc>http://www.arrivalsoflondon.co.uk/{stop.url}</loc>
      <lastmod>{current_date}</lastmod>
      <changefreq>always</changefreq>
   </url>""")

    f.write("\n</urlset>")
    f.close()
    print(f"Added {len(added_urls)} stops")
if __name__ == '__main__':
    main()
