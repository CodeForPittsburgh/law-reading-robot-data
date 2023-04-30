from datetime import datetime
from typing import List

from pydantic import BaseModel


class BaseGet(BaseModel):
    created_at: datetime
    updated_at: datetime | None


# HouseBill Schema
class HouseBillBase(BaseModel):
    hb_id: str
    title: str
    title_detail: dict[str, str]
    links: List[dict[str, str]]
    link: str
    summary: str
    summary_detail: dict[str, str]
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
    id: str

    class Config:
        orm_mode = True


class HouseBillGet(HouseBill, BaseGet):
    pass


class HouseBillCreate(HouseBillBase):
    pass
