import unittest

from db_interfaces.PostgresDBInterface import PostgresDBInterface
from law_reader.common.RevisionSummaryInfo import RevisionSummaryInfo

class TestPostgresDBInterface(unittest.TestCase):

        def setUp(self):
            # Connect to Database Dev
            self.db_interface = PostgresDBInterface(
                db_password="postgres",
                db_host="localhost")

        def test_get_tables(self):
            # Get the tables in the database
            tables = self.db_interface.get_tables()
            # Check that certain key tables are in the database
            self.assertIn(("Bills",), tables)
            self.assertIn(("Revisions",), tables)
            self.assertIn(("Revision_Text",), tables)
            self.assertIn(("Summaries",), tables)
            self.assertIn(("Active_Summaries",), tables)

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
            bill_id = "11110SB111"
            revision_id = "11110SB111P2222"
            # Insert a row into the Bills table
            test_row = {
                "legislative_id": bill_id,
                "bill_number": "111",
                "session_type": "0",
                "chamber": "Senate",
                "legislative_session": "1111",
            }
            self.db_interface.insert("Bills", test_row)

            # Insert a row into the Revisions Table
            revisions_row = {
                "bill_id": bill_id,
                "printer_no": "2222",
                "full_text_link": "https://www.fakeurl.com/abc123xyz",
                "publication_date": "2021-01-01",
                "revision_guid": revision_id,
                "description": "test",
            }
            self.db_interface.insert("Revisions", revisions_row)

            # Upload a summary
            test_summary = "This is a test summary"
            summary_id = self.db_interface.upload_summary(revision_id, test_summary)
            # Check that the summary was uploaded
            self.db_interface.execute("SELECT * FROM \"Summaries\" WHERE id = %s", (summary_id,))
            result = self.db_interface.fetchone()
            self.assertIn(test_summary, result)

        def test_download_bill_text(self):
            # Insert a row into the Bills table
            bill_id = "11110SB111"
            revision_id = "11110SB111P2222"
            test_row = {
                "legislative_id": bill_id,
                "bill_number": "111",
                "session_type": "0",
                "chamber": "Senate",
                "legislative_session": "1111",
            }
            self.db_interface.insert("Bills", test_row)

            # Insert a row into the Revisions Table
            revisions_row = {
                "bill_id": bill_id,
                "printer_no": "2222",
                "full_text_link": "https://www.fakeurl.com/abc123xyz",
                "publication_date": "2021-01-01",
                "revision_guid": "11110SB111P2222",
                "description": "test",
            }
            self.db_interface.insert("Revisions", revisions_row)

            # Insert a row into the Revision_Text table
            revision_text_row = {
                "full_text": "This is a test",
                "revision_guid": revision_id
            }
            self.db_interface.insert("Revision_Text", revision_text_row)

            # Download the bill text
            text = self.db_interface.download_bill_text(revision_id)
            self.assertIn("This is a test", text)

        def test_get_revisions_without_summaries(self):
            # Insert a row into the Bills table
            bill_id = "11110SB111"
            test_row = {
                "legislative_id": bill_id,
                "bill_number": "111",
                "session_type": "0",
                "chamber": "Senate",
                "legislative_session": "1111",
            }
            self.db_interface.insert("Bills", test_row)

            # Insert a row into the Revisions Table
            revisions_row = {
                "bill_id": bill_id,
                "printer_no": "2222",
                "full_text_link": "https://www.fakeurl.com/abc123xyz",
                "publication_date": "2021-01-01",
                "revision_guid": "11110SB111P2222",
                "description": "test",
            }
            self.db_interface.insert("Revisions", revisions_row)

            # Get the revisions without summaries
            revisions = self.db_interface.get_revisions_without_summaries()
            self.assertIn("11110SB111P2222", revisions[0])

            # TODO: Update to also include revisions with summaries to further test