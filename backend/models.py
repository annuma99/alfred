"""
Pydantic models define what each endpoint promises to return. FastAPI
uses these to:
  1. Validate that DB rows actually match the shape we claim (catches
     bugs early instead of shipping malformed JSON to the frontend)
  2. Auto-generate interactive API docs at /docs
  3. Serialize DB rows -> clean JSON automatically
"""

from datetime import date, time
from typing import Optional
from pydantic import BaseModel


class CrimePin(BaseModel):
    """Lightweight shape for map pins -- one per crime, minimal fields."""
    cmplnt_num: str
    boro_nm: Optional[str]
    latitude: float
    longitude: float
    ofns_desc: Optional[str]
    law_cat_cd: Optional[str]
    cmplnt_fr_dt: Optional[date]


class CrimeDetail(BaseModel):
    """Full shape for the case detail panel, shown after a pin click."""
    cmplnt_num: str
    boro_nm: Optional[str]
    cmplnt_fr_dt: Optional[date]
    cmplnt_fr_tm: Optional[time]
    law_cat_cd: Optional[str]
    ofns_desc: Optional[str]
    pd_desc: Optional[str]
    prem_typ_desc: Optional[str]
    latitude: float
    longitude: float
    rpt_dt: Optional[date]
    ai_summary: Optional[str]


class BoroughCount(BaseModel):
    boro_nm: Optional[str]
    crime_count: int


class OffenseCount(BaseModel):
    ofns_desc: Optional[str]
    crime_count: int


class OffenseType(BaseModel):
    ofns_desc: str
    crime_count: int
