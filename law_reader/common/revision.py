from dataclasses import dataclass

"""
A read-only object to represent Revisions
"""


@dataclass
class Revision:
    bill_id: str
    printer_no: str
    full_text_link: str
    publication_date: str
    revision_guid: str
    description: str
