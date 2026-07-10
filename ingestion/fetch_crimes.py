"""
Talks to the NYC Open Data Socrata API for the NYPD Complaint Data
(Year to Date) dataset and returns clean, ready-to-insert records.

This is the ONLY file in the whole project that should ever make a
network call to data.cityofnewyork.us. Everything downstream (db.py,
summarize.py) just works with plain Python dicts.
"""

import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

SOCRATA_APP_TOKEN = os.environ["SOCRATA_APP_TOKEN"]
BASE_URL = "https://data.cityofnewyork.us/resource/5uac-w243.json"

# Only the fields we actually store. Trimming this keeps payloads small
# and keeps fetch_crimes.py in sync with the `crimes` table schema in db.py.
FIELDS = [
    "cmplnt_num", "boro_nm", "cmplnt_fr_dt", "cmplnt_fr_tm",
    "law_cat_cd", "ofns_desc", "pd_desc", "prem_typ_desc",
    "latitude", "longitude", "rpt_dt",
]


def fetch_recent_crimes(days_back=1, limit=5000):
    """
    Pulls every complaint REPORTED (not necessarily occurring) in the
    last `days_back` days. We filter on rpt_dt rather than cmplnt_fr_dt
    because a crime can occur weeks before it's reported -- for a daily
    ingestion job, "what's new in the system" is what we want, not
    "what happened yesterday."
    """
    since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00.000")

    params = {
        "$select": ",".join(FIELDS),
        "$where": f"rpt_dt >= '{since}' AND latitude != 0",
        "$order": "rpt_dt DESC",
        "$limit": limit,
    }
    headers = {"X-App-Token": SOCRATA_APP_TOKEN}

    response = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()

    raw_records = response.json()
    return [_clean_record(r) for r in raw_records]


def _clean_record(raw):
    """
    Socrata returns everything as strings, and dates come as full
    ISO timestamps (e.g. "2026-06-29T00:00:00.000"). Postgres wants
    proper DATE/TIME/FLOAT types, and missing fields need to become
    None rather than a missing dict key (psycopg2 needs every named
    param present).
    """
    return {
        "cmplnt_num": raw.get("cmplnt_num"),
        "boro_nm": raw.get("boro_nm"),
        "cmplnt_fr_dt": _parse_date(raw.get("cmplnt_fr_dt")),
        "cmplnt_fr_tm": raw.get("cmplnt_fr_tm"),
        "law_cat_cd": raw.get("law_cat_cd"),
        "ofns_desc": raw.get("ofns_desc"),
        "pd_desc": raw.get("pd_desc"),
        "prem_typ_desc": raw.get("prem_typ_desc"),
        "latitude": _parse_float(raw.get("latitude")),
        "longitude": _parse_float(raw.get("longitude")),
        "rpt_dt": _parse_date(raw.get("rpt_dt")),
    }


def _parse_date(value):
    if not value:
        return None
    # Socrata sends "2026-06-29T00:00:00.000" -- we only need the date part.
    return value.split("T")[0]


def _parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    # Quick manual test: `python fetch_crimes.py`
    # NOTE: this dataset publishes with a lag of a few months, so days_back=1
    # will often return nothing. Widen the window here just to confirm the
    # pull itself works end-to-end.
    records = fetch_recent_crimes(days_back=180)
    print(f"Fetched {len(records)} records")
    if records:
        print("Sample record:", records[0])