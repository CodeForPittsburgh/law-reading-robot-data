from supabase import create_client, Client
import feedparser
import os
import re
from enum import Enum
from dataclasses import dataclass

"""
File for extracting data from the RSS feeds of the PA Senate and House of Representatives
and loading it into Supabase.

The database tables updated by this script are:
    Bills
    Revisions
"""

#from dotenv import load_dotenv
#load_dotenv() #for local secret management with .env file

senate_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml"
house_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"

sb_api_url = "https://vsumrxhpkzegrktbtcui.supabase.co"
#sb_api_key = os.getenv("SUPABASE_API_KEY") #local secret management wtih .env file
#sb_api_key = os.environ["SUPABASE_API_KEY"] #github actions secret management


class LegislativeBody(Enum):
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
    "title": "",
    "description": "",
    "legislative_id": "",
}

class BillIdentifier:
    """
    Extracts unique information from a bill's guid and embeds them in discrete properties
    """

    @staticmethod
    def extract_bill_guid(revision_guid):
        return re.search("BillGuid=(.*)", revision_guid).group(1)

    @staticmethod
    def determine_chamber(chamber_letter):
        if chamber_letter == "H":
            return "House"
        elif chamber_letter == "S":
            return "Senate"
        else:
            raise Exception("Invalid chamber letter in guid")

    def __init__(self, guid):
        self.guid = guid
        self.bill_guid = re.search(r"(\d{4}\d[H|S]B\d+)P\d+", guid).group(1)
        re_result = re.search(r"(\d{4})(\d)(H|S)B(\d+)P(\d+)", guid)
        self.legislative_session = re_result.group(1)
        self.session_type = re_result.group(2)
        self.chamber = self.determine_chamber(re_result.group(3))
        self.bill_number = re_result.group(4)
        self.printer_number = re_result.group(5)


class OutputRecord:

    def __init__(self, supa_con, table_name, output_dict):
        self.supa_con = supa_con
        self.table_name = table_name
        self.output_dict = output_dict.copy()

    def has_existing_supabase_records(self, matching_columns):
        # TODO: This might suffice for now, but selecting every row in the table is not a good long-term solution
        statement = self.supa_con.table(self.table_name).select("*", count="exact")
        for column in matching_columns:
            statement = statement.eq(column, self.output_dict[column])
        existing_bill_records = statement.execute()
        return existing_bill_records.count > 0


class Extractor:

    def __init__(self, supa_con, leg_body, rss_feed):
        self.supa_con = supa_con
        self.leg_body = leg_body
        self.rss_feed = rss_feed

    def extract_metadata_from_rss_feed(self, max_attempts=3):
        rss_feed = feedparser.parse(self.rss_feed)
        attempt_count = 0
        for bill in rss_feed.entries:
            if bill is None:
                continue

            bill_identifier = BillIdentifier(bill["guid"])
            self.create_and_attempt_to_insert_bill(bill, bill_identifier)
            self.create_and_attempt_to_insert_revision(bill, bill_identifier)
            attempt_count += 1
            if attempt_count >= max_attempts:
                break

    def create_and_attempt_to_insert_revision(self, bill, bill_identifier: BillIdentifier):
        revisions_output_record = self.create_revisions_output_record(bill, bill_identifier)
        if not revisions_output_record.has_existing_supabase_records(["revision_guid"]):
            self.insert_new_record(revisions_output_record)


    def create_and_attempt_to_insert_bill(self, bill, bill_identifier: BillIdentifier):
        bills_output_record = self.create_bill_output_record(bill, bill_identifier)
        if not bills_output_record.has_existing_supabase_records(["legislative_id"]):
            self.insert_new_record(bills_output_record)

    # Method to obtain bill internal id from existing supabase row for a bill
    def get_bill_internal_id(self, bill_identifier: BillIdentifier):
        statement = self.supa_con.table("Bills").select("bill_internal_id").eq("legislative_id", bill_identifier.bill_guid)
        bill_internal_id = statement.execute()
        return bill_internal_id

    def create_revisions_output_record(self, bill, bill_identifier: BillIdentifier):
        revisions_output_record = OutputRecord(self.supa_con, "Revisions", REVISIONS_OUTPUT_DICT)
        revisions_output_record.output_dict["bill_internal_id"] = self.get_bill_internal_id(bill_identifier)
        revisions_output_record.output_dict["printer_no"] = bill_identifier.printer_number
        revisions_output_record.output_dict["full_text_link"] = bill["link"]
        revisions_output_record.output_dict["publication_date"] = bill["published"]
        revisions_output_record.output_dict["revision_guid"] = bill["guid"]
        revisions_output_record.output_dict["description"] = bill["description"]
        return revisions_output_record

    def create_bill_output_record(self, bill, bill_identifier: BillIdentifier):
        bills_output_record = OutputRecord(self.supa_con, "Bills", BILL_OUTPUT_DICT)
        bills_output_record.output_dict["bill_number"] = bill_identifier.bill_number
        bills_output_record.output_dict["title"] = bill.title
        bills_output_record.output_dict["description"] = bill.description
        bills_output_record.output_dict["legislative_id"] = bill_identifier.bill_guid
        bills_output_record.output_dict["legislative_session"] = bill_identifier.legislative_session
        bills_output_record.output_dict["session_type"] = bill_identifier.session_type
        bills_output_record.output_dict["chamber"] = bill_identifier.chamber
        return bills_output_record

    def get_bill_and_printer_no(self, title):
        bp_regex = f"({self.leg_body}) (Bill|Resolution) (\d+) (Printer's Number) (\d+)"
        result = re.search(bp_regex, title)
        return result.group(3), result.group(5)

    def insert_new_record(self, out_rec: OutputRecord):
        self.supa_con.table(out_rec.table_name).insert(out_rec.output_dict).execute()

def extract_from_rss_feed(supabase_connection, leg_bod, rss_feed):
    extractor = Extractor(supabase_connection, leg_bod, rss_feed)
    extractor.extract_metadata_from_rss_feed()

if __name__ == "__main__":
    supabase_connection: Client = create_client(sb_api_url, sb_api_key)
    extract_from_rss_feed(supabase_connection, LegislativeBody.SENATE, senate_rss_feed)
    extract_from_rss_feed(supabase_connection, LegislativeBody.HOUSE, house_rss_feed)