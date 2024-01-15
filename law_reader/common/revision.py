from dataclasses import dataclass
from typing import Optional

"""
A read-only object to represent Revisions
"""


@dataclass
class Revision:
    revision_guid: str
    printer_no: Optional[str] = None
    full_text_link: Optional[str] = None
    publication_date: Optional[str] = None
    description: Optional[str] = None
