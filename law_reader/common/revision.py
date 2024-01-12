from dataclasses import dataclass

"""
A read-only object to represent Revisions
"""


@dataclass
class Revision:
    printer_no: str
    full_text_link: str
    publication_date: str
    revision_guid: str
    description: str
