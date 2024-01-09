import os
import unittest

from db_interfaces.PostgresDBInterface import PostgresDBInterface
from law_reader import BillIdentifier, Revision
from law_reader.common.RevisionSummaryInfo import RevisionSummaryInfo

class TestPostgresDBInterface(unittest.TestCase):


        def setUp(self):
            # Create a PostgresDBInterface object
            self.db_interface = PostgresDBInterface(
                db_password=os.environ.get("SUPABASE_DB_PASSWORD"),
                db_host=os.environ.get("SUPABASE_DB_HOST"),
                port=os.environ.get("SUPABASE_DB_PORT")
            )
            # Truncate the tables in the database
            for table in ["Bills", "Revisions", "Revision_Text", "Summaries"]:
                self.db_interface.execute("TRUNCATE TABLE \"{}\" CASCADE".format(table))

        def generate_fake_bill_and_revision(self):
            bill_identifier = BillIdentifier(
                revision_guid="11110SB111P2222",
            )
            revision = Revision(
                bill_internal_id="FakeID",
                printer_no="2222",
                full_text_link="https://www.fakeurl.com/abc123xyz",
                publication_date="2021-01-01",
                revision_guid="11110SB111P2222",
                description="test",
            )
            return bill_identifier, revision

        def test_get_tables(self):
            # Get the tables in the database
            tables = self.db_interface.get_tables()
            # Check that certain key tables are in the database
            for table in ["Bills", "Revisions", "Revision_Text", "Summaries"]:
                self.assertIn((table,), tables)

        def test_insert(self):
            bill_id = "11110SB111"
            test_row = {
                "legislative_id": bill_id,
                "bill_number": "111",
                "session_type": "0",
                "chamber": "Senate",
                "legislative_session": "1111",
            }
            # Insert a row into the Bills table
            self.db_interface.insert("Bills", test_row)
            # Check that the row was inserted
            self.db_interface.execute("SELECT * FROM \"Bills\" WHERE legislative_id = %s", (bill_id,))
            result = self.db_interface.fetchone()
            self.assertIn(test_row["legislative_id"], result)

        def test_upload_summary(self):
            bill_identifier, revision = self.generate_fake_bill_and_revision()
            self.db_interface.add_revision(bill_identifier, revision)
            revision_id = bill_identifier.revision_guid

            # Upload a summary
            test_summary = "This is a test summary"
            summary_id = self.db_interface.upload_summary(revision_id, test_summary)
            # Check that the summary was uploaded
            self.db_interface.execute("SELECT * FROM \"Summaries\" WHERE summary_id = %s", (summary_id,))
            result = self.db_interface.fetchone()
            self.assertIn(test_summary, result)

        def test_update(self):
            bill_id = "11110SB111"
            test_row = {
                "legislative_id": bill_id,
                "bill_number": "111",
                "session_type": "0",
                "chamber": "Senate",
                "legislative_session": "1111",
            }
            # Insert a row into the Bills table
            self.db_interface.insert("Bills", test_row)
            # Check that the row was inserted
            self.db_interface.execute("SELECT * FROM \"Bills\" WHERE legislative_id = %s", (bill_id,))
            result = self.db_interface.fetchone()
            self.assertIn(test_row["legislative_id"], result)

            # Update the row
            test_row["bill_number"] = "222"
            self.db_interface.update(
                table="Bills",
                row_column_dict=test_row,
                where_conditions={"legislative_id": bill_id},
                )
            # Check that the row was updated
            self.db_interface.execute("SELECT * FROM \"Bills\" WHERE legislative_id = %s", (bill_id,))
            result = self.db_interface.fetchone()
            self.assertIn(int(test_row["bill_number"]), result)

        def test_insert_and_link(self):
            bill_identifier, revision = self.generate_fake_bill_and_revision()
            self.db_interface.add_revision(bill_identifier, revision)
            revision_id = bill_identifier.revision_guid

            # Insert a row into the Revision_Text table and link it to the Revisions table
            revision_text_row = {
                "full_text": "This is a test",
            }
            self.db_interface.insert_and_link(
                row_to_insert=revision_text_row,
                table_to_insert_into="Revision_Text",
                column_to_return="rt_unique_id",
                linking_table="Revisions",
                linking_column_to_update="rt_unique_id",
                linking_where={"revision_guid": revision_id}
            )

        def test_download_bill_text(self):
            bill_identifier, revision = self.generate_fake_bill_and_revision()
            self.db_interface.add_revision(bill_identifier, revision)
            revision_id = bill_identifier.revision_guid

            # Insert a row into the Revision_Text table and link it to the Revisions table
            revision_text_row = {
                "full_text": "This is a test",
            }
            self.db_interface.insert_and_link(
                row_to_insert=revision_text_row,
                table_to_insert_into="Revision_Text",
                column_to_return="rt_unique_id",
                linking_table="Revisions",
                linking_column_to_update="rt_unique_id",
                linking_where={"revision_guid": revision_id}
            )

            # Download the bill text
            text = self.db_interface.download_bill_text(revision_id)
            self.assertIn("This is a test", text)

        def test_get_revisions_without_summaries(self):
            bill_identifier, revision = self.generate_fake_bill_and_revision()
            self.db_interface.add_revision(bill_identifier, revision)

            # Get the revisions without summaries
            revisions = self.db_interface.get_revisions_without_summaries()
            self.assertIn(bill_identifier.revision_guid, revisions[0])

            # TODO: Update to also include revisions with summaries to further test

        def test_add_revision(self):
            bill_identifier, revision = self.generate_fake_bill_and_revision()
            self.db_interface.add_revision(bill_identifier, revision)
            # Check that the row was inserted
            self.db_interface.execute("SELECT * FROM \"Revisions\" WHERE revision_guid = %s", (bill_identifier.revision_guid,))