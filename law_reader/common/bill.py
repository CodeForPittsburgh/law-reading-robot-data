from dataclasses import dataclass

from .bill_identifier import LegislativeChamber

"""
A read-only object to represent Bills
"""


@dataclass
class Bill:
    bill_number: str
    legislative_id: str
    legislative_session: str
    session_type: str
    chamber: LegislativeChamber
