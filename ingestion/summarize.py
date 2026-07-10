"""
Generates a short, plain-language summary for each crime record that
doesn't have one yet, using the Claude API.

This runs AFTER new records are written to the DB (see run_daily.py),
never before -- we only want to spend API calls on records we're
actually going to keep and show.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = (
    "You summarize NYPD complaint records for a public crime map. "
    "Write ONE plain, neutral sentence describing what was reported. "
    "Do not speculate beyond the given fields. Do not include the "
    "complaint number. No preamble, just the sentence."
)


def summarize_record(record):
    """
    record: dict with ofns_desc, pd_desc, prem_typ_desc, boro_nm,
    cmplnt_fr_dt, cmplnt_fr_tm (matches db.get_unsummarized() output)
    """
    prompt = (
        f"Offense category: {record['ofns_desc']}\n"
        f"Specific offense: {record['pd_desc']}\n"
        f"Location type: {record['prem_typ_desc']}\n"
        f"Borough: {record['boro_nm']}\n"
        f"Date: {record['cmplnt_fr_dt']} at {record['cmplnt_fr_tm']}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def summarize_batch(conn, db_module, batch_size=50):
    """
    Pulls up to `batch_size` unsummarized rows, generates a summary for
    each, and writes it back immediately (one at a time, not bulk) so
    that if the job dies halfway through, already-summarized rows
    aren't redone on the next run.
    """
    records = db_module.get_unsummarized(conn, limit=batch_size)
    count = 0
    for record in records:
        try:
            summary = summarize_record(record)
            db_module.save_summary(conn, record["cmplnt_num"], summary)
            count += 1
        except Exception as e:
            # One bad record shouldn't kill the whole batch.
            print(f"Failed to summarize {record['cmplnt_num']}: {e}")
    return count