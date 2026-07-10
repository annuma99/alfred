"""
Read-only database access for the API.

Unlike ingestion's db.py (which opens one connection, does its work,
and exits once a day), a web server needs to handle many requests at
once -- so this uses a connection POOL: a small set of open connections
that get borrowed and returned per-request instead of opening a fresh
connection every time (slow) or sharing one connection across requests
(unsafe with concurrent traffic).
"""

import os
from contextlib import contextmanager
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

# minconn=1, maxconn=10 -- plenty for a small app; raise maxconn later
# if you start seeing "connection pool exhausted" under real traffic.
connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)


@contextmanager
def get_cursor():
    """
    Usage:
        with get_cursor() as cur:
            cur.execute(...)
            rows = cur.fetchall()

    Borrows a connection from the pool, hands back a dict-returning
    cursor, and always returns the connection to the pool when done --
    even if the query raises an error.
    """
    conn = connection_pool.getconn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
    finally:
        connection_pool.putconn(conn)


# --- Query functions -------------------------------------------------
# Routes call these instead of writing SQL inline, so the query logic
# stays in one place and routes just handle HTTP concerns (params,
# status codes, response shaping).

TIME_RANGE_DAYS = {"day": 1, "week": 7, "month": 30}


def get_pins(borough=None, time_range="week"):
    """
    Lightweight rows for map pins: just enough to place and label a pin,
    NOT the full case detail (keeps payload small when there are
    hundreds of pins on screen at once).
    """
    days = TIME_RANGE_DAYS.get(time_range, 7)

    query = """
        SELECT cmplnt_num, boro_nm, latitude, longitude, ofns_desc, law_cat_cd, cmplnt_fr_dt
        FROM crimes
        WHERE rpt_dt >= (SELECT MAX(rpt_dt) FROM crimes) - INTERVAL '%s days'
    """
    params = [days]

    if borough:
        query += " AND boro_nm = %s"
        params.append(borough.upper())

    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def get_crime_detail(cmplnt_num):
    """
    Full record for the case detail panel -- includes the AI summary
    generated during ingestion.
    """
    query = "SELECT * FROM crimes WHERE cmplnt_num = %s"
    with get_cursor() as cur:
        cur.execute(query, [cmplnt_num])
        return cur.fetchone()


def get_borough_summary():
    """
    Count of records per borough, for a landing-state overview before
    a user drills into a specific borough.
    """
    query = """
        SELECT boro_nm, COUNT(*) as crime_count
        FROM crimes
        WHERE rpt_dt >= (SELECT MAX(rpt_dt) FROM crimes) - INTERVAL '30 days'
        GROUP BY boro_nm
        ORDER BY boro_nm
    """
    with get_cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def get_borough_offense_breakdown(borough):
    """
    Count of records per offense type, for one borough -- powers a
    small chart/breakdown on that borough's summary view.
    """
    query = """
        SELECT ofns_desc, COUNT(*) as crime_count
        FROM crimes
        WHERE boro_nm = %s
          AND rpt_dt >= (SELECT MAX(rpt_dt) FROM crimes) - INTERVAL '30 days'
        GROUP BY ofns_desc
        ORDER BY crime_count DESC
        LIMIT 10
    """
    with get_cursor() as cur:
        cur.execute(query, [borough.upper()])
        return cur.fetchall()