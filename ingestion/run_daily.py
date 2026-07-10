"""
Entry point for the daily ingestion job.

Order of operations matters here:
  1. Make sure the table exists (cheap no-op after the first run)
  2. Fetch new/updated records from Socrata
  3. Upsert them into Postgres
  4. Generate AI summaries for anything that doesn't have one yet

This is the one script you point cron / GitHub Actions / a scheduled
serverless function at. Everything else in this folder is a module it
imports.
"""

import db
import fetch_crimes
import summarize


def main():
    conn = db.get_connection()
    db.ensure_schema(conn)

    print("Fetching recent crimes from NYC Open Data...")
    # This dataset publishes with a real lag (NYPD data can trail by
    # months), so "daily ingestion" means "catch whatever's newly
    # published," not "yesterday's crimes." A wider window costs nothing
    # extra here since db.py's upsert skips records you already have.
    records = fetch_crimes.fetch_recent_crimes(days_back=200)
    print(f"  -> {len(records)} records fetched")

    print("Writing to database...")
    inserted, updated = db.upsert_crimes(conn, records)
    print(f"  -> {inserted} new, {updated} updated")

    print("Generating AI summaries for new records...")
    summarized = summarize.summarize_batch(conn, db)
    print(f"  -> {summarized} summaries generated")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()