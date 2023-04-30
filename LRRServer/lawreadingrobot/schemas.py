from datetime import datetime
from typing import Any, List

import orjson
from pydantic import BaseModel


def orjson_dumps(v: Any, *, default: Any) -> str:
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


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

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class HouseBill(HouseBillBase):
    id: str


class HouseBillGet(HouseBill, BaseGet):
    pass


class HouseBillCreate(HouseBillBase):
    pass
