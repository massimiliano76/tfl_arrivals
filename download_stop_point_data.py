from tfl_arrivals import db
from tfl_arrivals.models import *
from tfl_arrivals import fetcher
from tfl_arrivals import config
import logging
from threading import Thread, Semaphore, Lock

set_lock = Lock()
downloaded_stops = set()
semaphore = Semaphore(10)
def get_stop(naptan_id):
    set_lock.acquire()
    if naptan_id in downloaded_stops:
        set_lock.release()
        semaphore.release()
        return
    set_lock.release()

    downloaded_stops.add(naptan_id)
    new_stops = fetcher.fetch_stops(naptan_id)

    set_lock.acquire()
    for ns in new_stops:
        downloaded_stops.add(ns.naptan_id)
    set_lock.release()
    semaphore.release()

def main():
    config["app"]["cache_api_responses"] = "True"
    config["app"]["use_api_response_cache"] = "True"

    stop_file = open("stop_point_naptan_ids", "r")

    all_stops = [l.strip() for l in stop_file.readlines()]
    count = 0
    for s in all_stops:
        semaphore.acquire()

        count += 1
        set_lock.acquire()
        size =  len(downloaded_stops)
        set_lock.release()
        print(f"-------- Stop #{count}: {s}, downloaded: {size}")
        t = Thread(target=get_stop, args=(s,))
        t.start()

if __name__ == '__main__':
    main()
