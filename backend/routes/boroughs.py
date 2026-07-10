"""
Endpoints for borough-level aggregates -- powers an "at a glance" view
before a user drills into individual pins.
"""

from typing import List
from fastapi import APIRouter

import db
from models import BoroughCount, OffenseCount

router = APIRouter(prefix="/boroughs", tags=["boroughs"])


@router.get("", response_model=List[BoroughCount])
def list_boroughs():
    """
    GET /boroughs

    Crime counts per borough over the last 30 days (relative to the
    most recent data available, not today's calendar date -- see the
    ingestion lag note in the project notes). Good for a landing-state
    map view: shade/size each borough before anything is clicked.
    """
    return db.get_borough_summary()


@router.get("/{borough}/breakdown", response_model=List[OffenseCount])
def borough_breakdown(borough: str):
    """
    GET /boroughs/{borough}/breakdown

    Top offense types for one borough -- e.g. for a small bar chart
    shown when a borough is selected, before zooming into individual pins.
    """
    return db.get_borough_offense_breakdown(borough)