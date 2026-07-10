"""
Handles all Postgres interaction for the ingestion pipeline.

Responsibilities:
- Open/close a connection using DATABASE_URL from .env
- Create the `crimes` table if it doesn't exist (safe to run every time)
- Upsert incoming records (insert new ones, update existing ones if the
  source data changed, e.g. NYPD reclassifies an offense after the fact)
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

# The schema mirrors the fields we pull from Socrata, plus two of our own:
# ai_summary (filled in later by summarize.py) and ingested_at (bookkeeping).
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS crimes (
    cmplnt_num      TEXT PRIMARY KEY,
    boro_nm         TEXT,
    cmplnt_fr_dt    DATE,
    cmplnt_fr_tm    TIME,
    law_cat_cd      TEXT,
    ofns_desc       TEXT,
    pd_desc         TEXT,
    prem_typ_desc   TEXT,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    rpt_dt          DATE,
    ai_summary      TEXT,
    ingested_at     TIMESTAMPTZ DEFAULT now()
);
"""

# ON CONFLICT means: if a cmplnt_num we've already stored comes back again
# (e.g. NYPD corrects a record), overwrite the fields but leave ai_summary
# alone so we don't burn API calls re-summarizing unchanged cases.
UPSERT_SQL = """
INSERT INTO crimes (
    cmplnt_num, boro_nm, cmplnt_fr_dt, cmplnt_fr_tm, law_cat_cd,
    ofns_desc, pd_desc, prem_typ_desc, latitude, longitude, rpt_dt
) VALUES (
    %(cmplnt_num)s, %(boro_nm)s, %(cmplnt_fr_dt)s, %(cmplnt_fr_tm)s, %(law_cat_cd)s,
    %(ofns_desc)s, %(pd_desc)s, %(prem_typ_desc)s, %(latitude)s, %(longitude)s, %(rpt_dt)s
)
ON CONFLICT (cmplnt_num) DO UPDATE SET
    boro_nm = EXCLUDED.boro_nm,
    law_cat_cd = EXCLUDED.law_cat_cd,
    ofns_desc = EXCLUDED.ofns_desc,
    pd_desc = EXCLUDED.pd_desc,
    prem_typ_desc = EXCLUDED.prem_typ_desc,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    rpt_dt = EXCLUDED.rpt_dt
RETURNING cmplnt_num, (xmax = 0) AS inserted;
"""

# Grabs rows that don't have a summary yet, so summarize.py knows what's new.
SELECT_UNSUMMARIZED_SQL = """
SELECT cmplnt_num, ofns_desc, pd_desc, prem_typ_desc, boro_nm, cmplnt_fr_dt, cmplnt_fr_tm
FROM crimes
WHERE ai_summary IS NULL
LIMIT %(limit)s;
"""

UPDATE_SUMMARY_SQL = """
UPDATE crimes SET ai_summary = %(summary)s WHERE cmplnt_num = %(cmplnt_num)s;
"""


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
    conn.commit()


def upsert_crimes(conn, records):
    """
    records: list of dicts with keys matching the Socrata field names
    (cmplnt_num, boro_nm, cmplnt_fr_dt, ...)

    Returns (num_inserted, num_updated) so run_daily.py can log a clean summary.
    """
    inserted = 0
    updated = 0
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        for record in records:
            cur.execute(UPSERT_SQL, record)
            result = cur.fetchone()
            if result["inserted"]:
                inserted += 1
            else:
                updated += 1
    conn.commit()
    return inserted, updated


def get_unsummarized(conn, limit=50):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(SELECT_UNSUMMARIZED_SQL, {"limit": limit})
        return cur.fetchall()


def save_summary(conn, cmplnt_num, summary):
    with conn.cursor() as cur:
        cur.execute(UPDATE_SUMMARY_SQL, {"cmplnt_num": cmplnt_num, "summary": summary})
    conn.commit()