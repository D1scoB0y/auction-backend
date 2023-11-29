import datetime as dt
import pytz


intervals = [
    (10, 1),
    (100, 5),
    (200, 10),
    (500, 20),
    (1000, 50),
    (2000, 100),
    (5000, 200),
    (10000, 400),
    (20000, 1000),
    (50000, 2500),
    (100000, 5000),
    (200000, 10000),
    (500000, 20000),
]


def next_minimal_bid(current_bid: int) -> int:
    for interval in intervals:
        if current_bid <= interval[0]:
            return current_bid + interval[1]
    return current_bid + 40_000


def current_datetime() -> dt.datetime:
    """Returns utc datetime"""
    return dt.datetime.now(tz=pytz.utc).replace(tzinfo=None)
