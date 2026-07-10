"""
Endpoints for individual crime records: the list of pins for the map,
and the full detail for one case when a pin is clicked.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

import db
from models import CrimePin, CrimeDetail, OffenseType

router = APIRouter(prefix="/crimes", tags=["crimes"])


@router.get("", response_model=List[CrimePin])
def list_crimes(
    borough: Optional[str] = Query(None, description="e.g. Brooklyn, Queens"),
    range: str = Query("week", description="day | week | month"),
    offense: Optional[str] = Query(None, description="e.g. ROBBERY, GRAND LARCENY"),
):
    """
    GET /crimes?borough=Brooklyn&range=week&offense=ROBBERY

    Returns the pins to plot on the map. Deliberately lightweight --
    just enough fields to place and label a pin. Full details are a
    separate call (GET /crimes/{id}) so we're not shipping the whole
    case record for every one of potentially hundreds of pins on screen.
    """
    if range not in db.TIME_RANGE_DAYS:
        raise HTTPException(status_code=400, detail="range must be one of: day, week, month")

    return db.get_pins(borough=borough, time_range=range, offense=offense)


@router.get("/offense-types", response_model=List[OffenseType])
def list_offense_types():
    """
    GET /crimes/offense-types

    Distinct offense categories present in the data, most common first --
    powers the crime-type filter dropdown. NOTE: this route must stay
    declared before GET /crimes/{cmplnt_num} below, or FastAPI will match
    "offense-types" as a cmplnt_num path param instead of this route.
    """
    return db.get_offense_types()


@router.get("/{cmplnt_num}", response_model=CrimeDetail)
def get_crime(cmplnt_num: str):
    """
    GET /crimes/{cmplnt_num}

    Returns full case detail + the AI-generated summary, for the panel
    shown after a user clicks a specific pin.
    """
    record = db.get_crime_detail(cmplnt_num)
    if record is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return record
