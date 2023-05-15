import uuid
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class BaseGet(BaseModel):
    created_at: datetime
    updated_at: datetime | None


# HouseBill Schema
class HouseBillBase(BaseModel):
    hb_id: str
    title: str
    link: str
    summary: str
    title_detail: Dict[str, str]
    links: List[Dict[str, str]]
    summary_detail: Dict[str, str]
    parss_primesponsor: str
    parss_cosponsors: str
    parss_lastaction: str
    parss_enacted: str
    parss_passedhouse: str
    parss_passedsenate: str
    published: str
    published_parsed: str
    guidislink: str


class HouseBill(HouseBillBase):
    pass

    class Config:
        orm_mode = True


class HouseBillGet(HouseBill, BaseGet):
    id: uuid.UUID


class HouseBillCreate(HouseBill):
    pass
