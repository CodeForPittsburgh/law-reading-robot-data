
import uuid

from sqlalchemy import JSON, Column, DateTime, Text, Uuid
from sqlalchemy.sql import func

from .database import Base


class BaseMixin(object):
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Makes sure the columns are added to the end of the table
    created_at._creation_order = 9998  # type: ignore
    updated_at._creation_order = 9999  # type: ignore


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


class HouseBill(Base, BaseMixin):
    __tablename__: str = 'housebill'

    id = Column(Uuid(as_uuid=True),
                primary_key=True,
                index=True,
                unique=True,
                default=new_uuid
                )
    hb_id = Column(Text, index=True)
    title = Column(Text, index=True)
    title_detail = Column(JSON)
    links = Column(JSON)
    link = Column(Text, index=True)
    summary = Column(Text, index=True)
    summary_detail = Column(JSON)
    # I think these fields will become relationships
    parss_primesponsor = Column(Text, index=True)
    parss_cosponsors = Column(Text, index=True)
    parss_lastaction = Column(Text, index=True)
    parss_enacted = Column(Text, index=True)
    parss_passedhouse = Column(Text, index=True)
    parss_passedsenate = Column(Text, index=True)
    # not these
    published = Column(Text, index=True)
    published_parsed = Column(Text, index=True)
    guidislink = Column(Text, index=True)
