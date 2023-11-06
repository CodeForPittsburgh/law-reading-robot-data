import re
from enum import Enum


class LegislativeChamber(Enum):
    """
    Enum for the legislative bodies of the Pennsylvania state legislature
    """
    SENATE = "Senate"
    HOUSE = "House"


class BillIdentifier:
    """
    Extracts unique information from a bill's guid and embeds them in discrete properties
    """

    @staticmethod
    def determine_chamber(chamber_letter: str) -> str:
        if chamber_letter == "H":
            return LegislativeChamber.HOUSE.value
        elif chamber_letter == "S":
            return LegislativeChamber.SENATE.value
        else:
            raise Exception("Invalid chamber letter in guid")

    def __init__(self, revision_guid: str):
        """
        :param revision_guid: The full guid of a bill revision, from which all other attributes are extracted.
        Attributes:
        -----------
        revision_guid: The full guid of a bill revision
        bill_guid: The guid of the bill itself, extracted from the revision guid
        legislative_session: The year of the legislative session, in YYYY format
        session_type: 0 for Regular Session or 1 for Special Session
        chamber: The chamber of the legislature ('House' or 'Senate')
        bill_number: Number assigned to the bill
        printer_number: Printer number of the bill
        """
        try:
            self.revision_guid = revision_guid
            # This regex function extracts the bill guid from the revision guid.
            # Effectively, it removes the printer number, which denotes a specific revision of a bill.
            self.bill_guid = re.search(r"(\d{4}\d[HS][RB]\d+)P\d+", revision_guid).group(1)
            # This regex function extracts multiple values from the revision guid. In order, these are:
            #   1: The year of the legislative session, in YYYY format (\d{4})
            #   2: 0 for Regular Session or 1 for Special Session (\d)
            #   3: The chamber of the legislature ('House' or 'Senate') (H|S)
            #   4: Number assigned to the bill: (\d+)
            #   5: Printer number of the bill: (\d+)
            #   Note additionally that [BR] indicates whether the revision is a [B]ill or a [R]esolution. This is not
            #    used in this script, but is included in the regex for completeness.
            re_result = re.search(r"(\d{4})(\d)(H|S)[BR](\d+)P(\d+)", revision_guid)
            self.legislative_session = re_result.group(1)
            self.session_type = re_result.group(2)
            self.chamber = self.determine_chamber(re_result.group(3))
            self.bill_number = re_result.group(4)
            self.printer_number = re_result.group(5)
        except AttributeError:
            raise Exception(f"Revision guid ({revision_guid}) does not correspond to expected regex format.")
