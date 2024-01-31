# Mock data for RSS feed and database responses
import os
import unittest
from unittest import mock

import feedparser

import law_reader.docx_etl as docx_etl
import law_reader.summarize_etl as summarize_etl
from law_reader.db_interfaces.PostgresDBInterface import PostgresDBInterface
from law_reader import Extractor

MOCK_RSS_FEED_DATA = {
    "entries": [
        {
            "guid": "20230SB1036P1313",
            "link": 'https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=HTM&sessYr=2023&sessInd=0&billBody=S&billTyp=B&billNbr=1036&pn=1313',
            "published": 'Mon, 08 Jan 2024 15:40:10 GMT',
            "description": "An Act amending the act of June 13, 1967 (P.L.31, No.21), known as the Human Services Code, providing for Office of Child Advocate, the Coalition of Trauma Prevention and Intervention and the Statewide Children's Mental Health Ombudsman; and imposing duties on the Department of Human Services...."

        },
        {
            "guid": "20230SB1036P1314",
            "link": 'https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=HTM&sessYr=2023&sessInd=0&billBody=S&billTyp=B&billNbr=1036&pn=1314',
            "published": 'Mon, 08 Jan 2024 15:40:10 GMT',
            "description": "An Act amending the act of June 13, 1967 (P.L.31, No.21), known as the Human Services Code, providing for Office of Child Advocate, the Coalition of Trauma Prevention and Intervention and the Statewide Children's Mental Health Ombudsman; and imposing duties on the Department of Human Services...."

        },
        {
            "guid": "20230SB1036P1315",
            "link": 'https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=HTM&sessYr=2023&sessInd=0&billBody=S&billTyp=B&billNbr=1036&pn=1315',
            "published": 'Mon, 08 Jan 2024 15:40:10 GMT',
            "description": "An Act amending the act of June 13, 1967 (P.L.31, No.21), known as the Human Services Code, providing for Office of Child Advocate, the Coalition of Trauma Prevention and Intervention and the Statewide Children's Mental Health Ombudsman; and imposing duties on the Department of Human Services...."

        }
    ]
}


class TestETLIntegration(unittest.TestCase):

    def setUp(self) -> None:
        self.db_interface = PostgresDBInterface()
        # Truncate the tables in the database (SupabaseDBInterface)
        tables = ['Revisions', 'Bills', 'Revision_Text', 'Summaries']
        # I cheat here and use the Postgres SQL library to do cascading deletes, as Supabase Python library does not support cascading deletes
        pg_interface = PostgresDBInterface()
        sql_script = ""
        for table in tables:
            sql_script += f"TRUNCATE \"{table}\" CASCADE;"
        pg_interface.cursor.execute(sql_script)
        pg_interface.commit()

    def tearDown(self):
        # Commit any uncommitted changes to the database
        self.db_interface.commit()

    # region Mocks
    @staticmethod
    def mock_rss_feed_parse(url):
        return feedparser.FeedParserDict(MOCK_RSS_FEED_DATA)

    @staticmethod
    def mock_convert_doc_to_docx(bill_path: str):
        """
        Creates a fake docx file in the same directory as the bill_path
        and returns the path to the fake docx file.
        """
        with open(bill_path.replace(".doc", ".docx"), "w") as f:
            f.write("Fake docx file")
        return bill_path.replace(".doc", ".docx")

    @staticmethod
    def side_effect_extract_law_text_from_docx():
        """
        Returns a unique string for each call.
        """
        count = 1
        while True:
            yield f"Text {count}"
            count += 1


    @staticmethod
    def mock_summarize_bill(bill_text: str) -> str:
        return f"Text's summary: {bill_text}"

    # endregion
    def test_end_to_end_workflow(self):
        #region rss_etl
        extractor = Extractor(self.db_interface, 'Senate', 'mock_rss_feed_url')
        with mock.patch('feedparser.parse', side_effect=self.mock_rss_feed_parse):
            # Perform the extraction
            extractor.extract_metadata_from_rss_feed(new_entry_count=3)

        # Check that the correct number of revisions were inserted into the revisions table
        result = self.db_interface.simple_select(
            table="Revisions",
            columns=["revision_guid"]
        )
        self.assertEqual(
            len(result),
            3,
            "The correct number of revisions were not inserted into the revisions table"
        )
        # # Check that the correct number of bills were inserted into the bills table
        result = self.db_interface.simple_select(
            table="Bills",
            columns=["legislative_id"]
        )
        self.assertEqual(
            len(result),
            1,
            "The correct number of bills were not inserted into the bills table"
        )
        #endregion
        #region docx_etl
        with mock.patch('law_reader.docx_etl.convert_doc_to_docx', new=self.mock_convert_doc_to_docx), \
                mock.patch('law_reader.docx_etl.extract_law_text_from_docx', side_effect=self.side_effect_extract_law_text_from_docx()):
            docx_etl.extract_and_upload_missing_bill_text(self.db_interface)

        # Check that the correct number of revision texts were uploaded to the database
        result = self.db_interface.simple_select(
            table="Revision_Text",
            columns=["rt_unique_id"]
        )
        self.assertEqual(
            len(result),
            3,
            "The correct number of revision texts were not inserted into the revision texts table"
        )

        # Check that the temporary files were deleted
        self.assertEquals(
            len(os.listdir("temp")),
            0,
            "Not all temporary files were deleted"
        )


        # Check that the correct number of revisions were updated in the revisions table
        result = self.db_interface.simple_select(
            table="Revisions",
            columns=["rt_unique_id"]
        )
        self.assertEqual(
            len(result),
            3,
            "The correct number of revisions were not updated in the revisions table"
        )
        # Check that each revision has a unique revision text
        result = self.db_interface.simple_select(
            table="Revision_Text",
            columns=["full_text"]
        )
        revision_texts = [row["full_text"] for row in result]
        self.assertEqual(
            len(set(revision_texts)),
            3,
            "Not all revisions have unique revision texts"
        )
        #endregion
        #region summary_etl
        with mock.patch('law_reader.summarize_etl.summarize_bill', new=self.mock_summarize_bill):
            summarize_etl.summarize_all_unsummarized_revisions(self.db_interface)

        # Check that the correct number of summaries were inserted into the summaries table
        result = self.db_interface.simple_select(
            table="Summaries",
            columns=["summary_id"]
        )
        self.assertEqual(
            len(result),
            3,
            "The correct number of summaries were not inserted into the summaries table"
        )

        # Check that each summary has a unique summary text
        result = self.db_interface.simple_select(
            table="Summaries",
            columns=["summary_text"]
        )
        summary_texts = [row["summary_text"] for row in result]
        self.assertEqual(
            len(set(summary_texts)),
            3,
            "Not all summaries have unique summary texts"
        )

        # Check that each summary references the correct revision
        result = self.db_interface.simple_select(
            table="Summaries",
            columns=["revision_internal_id"]
        )
        revision_ids = [row["revision_internal_id"] for row in result]
        self.assertEqual(
            len(set(revision_ids)),
            3,
            "Not all summaries reference the correct revision"
        )

        #endregion

