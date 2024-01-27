from dataclasses import asdict
import feedparser
import os

from law_reader.db_interfaces import DBInterface, SupabaseDBInterface, PostgresDBInterface
from law_reader.common import BillIdentifier, Bill, Revision, LegislativeChamber

"""
File for extracting data from the RSS feeds of the PA Senate and House of Representatives
and loading it into the database.

The database tables updated by this script are:
    Bills
    Revisions
"""

senate_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml"
house_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"

class InsertRecord:
    """
    A record to be inserted into a database table
    """

    def __init__(self, table_name: str, output_dict: dict):
        """
        :param table_name: The name of the table to insert into
        :param output_dict: A dictionary of column names and values to insert into the table
        """
        self.table_name = table_name
        self.output_dict = output_dict.copy()

    @staticmethod
    def insert_record_for_bill(bill: Bill) -> 'InsertRecord':
        return InsertRecord('Bills', asdict(bill))

    @staticmethod
    def insert_record_for_revision(revision: Revision) -> 'InsertRecord':
        return InsertRecord('Revisions', asdict(revision))


class Extractor:
    """
    Extracts data from the RSS feed of a Pennsylvania state legislative chamber and loads it into the database.
    """

    def __init__(self, db_interface: DBInterface, chamber: str, rss_feed):
        """
        :param chamber: The chamber of the legislature ('House' or 'Senate')
        :param rss_feed: The RSS feed of the chamber
        """
        self.chamber = chamber
        self.rss_feed = rss_feed
        self.db_interface: DBInterface = db_interface

    def extract_metadata_from_rss_feed(self, new_entry_count: int = 3):
        """
        Extracts metadata from the RSS feed of a Pennsylvania state legislative chamber and loads it into the database.
        :param new_entry_count: The number of new entries to extract from the RSS feed. Defaults to 3.
        """
        rss_feed = feedparser.parse(self.rss_feed)
        for bill in rss_feed.entries:
            if bill is None:
                continue

            bill_identifier = BillIdentifier(bill["guid"])
            bill_internal_id = self.create_and_attempt_to_insert_bill(bill_identifier)
            new_bill_insertion = bill_internal_id is not None
            new_revision_insertion = self.create_and_attempt_to_insert_revision(bill, bill_identifier, bill_internal_id)
            if new_bill_insertion or new_revision_insertion:
                new_entry_count -= 1
            if new_entry_count == 0:
                break

    def create_and_attempt_to_insert_revision(
            self,
            revision_rss_feed_entry,
            bill_identifier: BillIdentifier,
            bill_internal_id: str
    ) -> bool:
        """
        Creates a new bill revision record in the table "Revisions" if it does not already exist.
        :param revision_rss_feed_entry: The RSS feed entry for the bill revision
        :param bill_identifier: The BillIdentifier object for the bill
        :return: True if a new record was inserted, False if not
        """
        revisions_output_record = self.create_revisions_output_record(revision_rss_feed_entry, bill_identifier)
        if not self.db_interface.row_exists(
                table="Revisions",
                where_conditions={"revision_guid": revisions_output_record.output_dict["revision_guid"]}
        ):
            revisions_output_record.output_dict.update({"bill_internal_id": bill_internal_id})
            self.db_interface.insert(
                table="Revisions",
                row_column_dict=revisions_output_record.output_dict,
            )
            return True
        return False

    def create_and_attempt_to_insert_bill(self, bill_identifier: BillIdentifier) -> str:
        """
        Creates a new bill record in the table "Bills" if it does not already exist.
        :param bill_identifier: The BillIdentifier object for the bill
        :return: The bill_internal_id of the bill inserted, or the bill_internal_id of the bill already in the database
        """
        bills_output_record = self.create_bill_output_record(bill_identifier)
        if not self.db_interface.row_exists(
            table="Bills",
            where_conditions={"legislative_id": bills_output_record.output_dict["legislative_id"]},
        ):
            return self.db_interface.insert(
                table="Bills",
                row_column_dict=bills_output_record.output_dict,
                return_column="bill_internal_id"
            )
        return self.get_bill_internal_id(bill_identifier)

    def get_bill_internal_id(self, bill_identifier: BillIdentifier) -> str:
        """
        Gets the bill_internal_id of a bill from the table "Bills" using the bill's legislative_id.
        :param bill_identifier: The BillIdentifier object for the bill
        :return: The bill_internal_id of the bill
        """
        result = self.db_interface.simple_select(
            table="Bills",
            columns=["bill_internal_id"],
            where_conditions={"legislative_id": bill_identifier.bill_guid}
        )
        return result[0]["bill_internal_id"]

    def create_revisions_output_record(self, revision_rss_feed_entry, bill_identifier: BillIdentifier) -> InsertRecord:
        """
        Creates an OutputRecord for a bill revision, with the revision's metadata as properties.
        :param revision_rss_feed_entry: The RSS feed entry for the bill revision
        :param bill_identifier: The BillIdentifier object for the bill
        :return: An OutputRecord for the bill revision
        """
        revision = Revision(
            printer_no=bill_identifier.printer_number,
            full_text_link=revision_rss_feed_entry["link"],
            publication_date=revision_rss_feed_entry["published"],
            revision_guid=revision_rss_feed_entry["guid"],
            description=revision_rss_feed_entry["description"])
        return InsertRecord.insert_record_for_revision(revision)

    def create_bill_output_record(self, bill_identifier: BillIdentifier) -> InsertRecord:
        """
        Creates an OutputRecord for a bill, with the bill's metadata as properties.
        :param bill_identifier: The BillIdentifier object for the bill
        :return: An OutputRecord for the bill
        """
        bill = Bill(
            bill_number=bill_identifier.bill_number,
            legislative_id=bill_identifier.bill_guid,
            legislative_session=bill_identifier.legislative_session,
            session_type=bill_identifier.session_type,
            chamber=bill_identifier.chamber
        )
        return InsertRecord.insert_record_for_bill(bill)

    def insert_new_record(self, out_rec: InsertRecord):
        """
        Inserts a new record into the table specified by the OutputRecord's table_name property.
        :param out_rec: The OutputRecord to insert into the database
        """
        self.db_interface.insert(
            table=out_rec.table_name,
            row_column_dict=out_rec.output_dict
        )


def extract_from_rss_feed(leg_bod: str, rss_feed: str):
    db_interface = PostgresDBInterface.PostgresDBInterface()
    extractor = Extractor(
        db_interface=db_interface,
        chamber=leg_bod,
        rss_feed=rss_feed)
    extractor.extract_metadata_from_rss_feed()
    db_interface.commit()


if __name__ == "__main__":
    extract_from_rss_feed(LegislativeChamber.SENATE.value, senate_rss_feed)
    extract_from_rss_feed(LegislativeChamber.HOUSE.value, house_rss_feed)
