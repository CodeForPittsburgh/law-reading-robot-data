from supabase import create_client, Client
import feedparser
import os
import re
from enum import Enum

"""
File for extracting data from the RSS feeds of the PA Senate and House of Representatives
and loading it into Supabase.

The database tables updated by this script are:
    Bills
    Revisions
"""

senate_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml"
house_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"

DEBUG = True  # Set to True to print debug messages
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
sb_api_url = os.environ["SUPABASE_API_URL"]  # github actions secret management
sb_api_key = os.environ["SUPABASE_API_KEY"]  # github actions secret management


class LegislativeChamber(Enum):
    """
    Enum for the legislative bodies of the Pennsylvania state legislature
    """
    SENATE = "Senate"
    HOUSE = "House"


REVISIONS_OUTPUT_DICT = {
    "bill_internal_id": "",
    "printer_no": "",
    "full_text_link": "",
    "publication_date": "",
    "revision_guid": "",
    "description": "",
}

BILL_OUTPUT_DICT = {
    "bill_number": "",
    "legislative_session": "",
    "session_type": "",
    "chamber": "",
    "legislative_id": "",
}


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


class InsertRecord:
    """
    A record to be inserted into a Supabase table
    """

    def __init__(self, supa_con: Client, table_name: str, output_dict: dict):
        """
        :param supa_con: A Supabase connection object
        :param table_name: The name of the Supabase table to insert into
        :param output_dict: A dictionary of column names and values to insert into the Supabase table
        """
        self.supa_con = supa_con
        self.table_name = table_name
        self.output_dict = output_dict.copy()

    def exists_in_supabase(self, matching_columns):
        """
        Checks if a record already exists in the Supabase table specified by the OutputRecord's table_name property.
        :param matching_columns: A list of column names to match against the OutputRecord's output_dict property
        :return: True if a record exists, False if not
        """
        statement = self.supa_con.table(self.table_name).select("*", count="exact")
        for column in matching_columns:
            statement = statement.eq(column, self.output_dict[column])
        existing_bill_records = statement.execute()

        return existing_bill_records.count > 0


class Extractor:
    """
    Extracts data from the RSS feed of a Pennsylvania state legislative chamber and loads it into Supabase.
    """

    def __init__(self, supa_con: Client, chamber: str, rss_feed):
        """
        :param supa_con: A Supabase connection object
        :param chamber: The chamber of the legislature ('House' or 'Senate')
        :param rss_feed: The RSS feed of the chamber
        """
        self.supa_con = supa_con
        self.chamber = chamber
        self.rss_feed = rss_feed

    def extract_metadata_from_rss_feed(self, new_entry_count: int = 3):
        """
        Extracts metadata from the RSS feed of a Pennsylvania state legislative chamber and loads it into Supabase.
        :param new_entry_count: The number of new entries to extract from the RSS feed. Defaults to 3.
        """
        rss_feed = feedparser.parse(self.rss_feed)
        for bill in rss_feed.entries:
            if bill is None:
                continue

            bill_identifier = BillIdentifier(bill["guid"])
            new_bill_insertion = self.create_and_attempt_to_insert_bill(bill_identifier)
            new_revision_insertion = self.create_and_attempt_to_insert_revision(bill, bill_identifier)
            if new_bill_insertion or new_revision_insertion:
                new_entry_count -= 1
            if new_entry_count == 0:
                break

    def create_and_attempt_to_insert_revision(self, revision_rss_feed_entry, bill_identifier: BillIdentifier) -> bool:
        """
        Creates a new bill revision record in the Supabase table "Revisions" if it does not already exist.
        :param revision_rss_feed_entry: The RSS feed entry for the bill revision
        :param bill_identifier: The BillIdentifier object for the bill
        :return: True if a new record was inserted, False if not
        """
        revisions_output_record = self.create_revisions_output_record(revision_rss_feed_entry, bill_identifier)
        if not revisions_output_record.exists_in_supabase(["revision_guid"]):
            self.insert_new_record(revisions_output_record)
            return True
        return False

    def create_and_attempt_to_insert_bill(self, bill_identifier: BillIdentifier) -> bool:
        """
        Creates a new bill record in the Supabase table "Bills" if it does not already exist.
        :param bill_identifier: The BillIdentifier object for the bill
        :return: True if a new record was inserted, False if not
        """
        bills_output_record = self.create_bill_output_record(bill_identifier)
        if not bills_output_record.exists_in_supabase(["legislative_id"]):
            self.insert_new_record(bills_output_record)
            return True
        return False

    def get_bill_internal_id(self, bill_identifier: BillIdentifier) -> str:
        """
        Gets the bill_internal_id of a bill from the Supabase table "Bills" using the bill's legislative_id.
        :param bill_identifier: The BillIdentifier object for the bill
        :return: The bill_internal_id of the bill
        """
        statement = self.supa_con.table("Bills").\
            select("bill_internal_id").\
            eq("legislative_id", bill_identifier.bill_guid)
        api_response = statement.execute()
        return api_response.data[0]["bill_internal_id"]

    def create_revisions_output_record(self, revision_rss_feed_entry, bill_identifier: BillIdentifier) -> InsertRecord:
        """
        Creates an OutputRecord for a bill revision, with the revision's metadata as properties.
        :param revision_rss_feed_entry: The RSS feed entry for the bill revision
        :param bill_identifier: The BillIdentifier object for the bill
        :return: An OutputRecord for the bill revision
        """
        revisions_output_record = InsertRecord(self.supa_con, "Revisions", REVISIONS_OUTPUT_DICT)
        revisions_output_record.output_dict.update({
            "bill_internal_id": self.get_bill_internal_id(bill_identifier),
            "printer_no": bill_identifier.printer_number,
            "full_text_link": revision_rss_feed_entry["link"],
            "publication_date": revision_rss_feed_entry["published"],
            "revision_guid": revision_rss_feed_entry["guid"],
            "description": revision_rss_feed_entry["description"],
        })
        return revisions_output_record

    def create_bill_output_record(self, bill_identifier: BillIdentifier) -> InsertRecord:
        """
        Creates an OutputRecord for a bill, with the bill's metadata as properties.
        :param bill_identifier: The BillIdentifier object for the bill
        :return: An OutputRecord for the bill
        """
        bills_output_record = InsertRecord(self.supa_con, "Bills", BILL_OUTPUT_DICT)
        bills_output_record.output_dict.update({
            "bill_number": bill_identifier.bill_number,
            "legislative_id": bill_identifier.bill_guid,
            "legislative_session": bill_identifier.legislative_session,
            "session_type": bill_identifier.session_type,
            "chamber": bill_identifier.chamber,
        })
        return bills_output_record

    def insert_new_record(self, out_rec: InsertRecord):
        """
        Inserts a new record into the Supabase table specified by the OutputRecord's table_name property.
        :param out_rec: The OutputRecord to insert into Supabase
        """
        self.supa_con.table(out_rec.table_name).insert(out_rec.output_dict).execute()


def extract_from_rss_feed(supabase_client: Client, leg_bod: str, rss_feed: str):
    extractor = Extractor(supabase_client, leg_bod, rss_feed)
    extractor.extract_metadata_from_rss_feed()


if __name__ == "__main__":
    supabase_connection: Client = create_client(sb_api_url, sb_api_key)
    extract_from_rss_feed(supabase_connection, LegislativeChamber.SENATE.value, senate_rss_feed)
    extract_from_rss_feed(supabase_connection, LegislativeChamber.HOUSE.value, house_rss_feed)
