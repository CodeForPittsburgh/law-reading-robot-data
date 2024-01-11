import unittest
from unittest import mock

import feedparser

from law_reader import SupabaseDBInterface, Extractor

# Mock data for RSS feed and database responses
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

class TestRSSETL(unittest.TestCase):

    def setUp(self) -> None:
        self.db_interface = SupabaseDBInterface()
        self.extractor = Extractor(self.db_interface, 'Senate', 'mock_rss_feed_url')
        # Truncate the tables in the database (SupabaseDBInterface)
        table_columns = [
            ("Revisions", "revision_guid"),
            ("Bills", "legislative_id"),
            ("Revision_Text", "rt_unique_id"),
            ("Summaries", "summary_id")
        ]

        for table, column in table_columns:
            self.db_interface.supabase_connection.table(table).delete().neq(column, "-1").execute()

    def mock_rss_feed_parse(self, url):
        return feedparser.FeedParserDict(MOCK_RSS_FEED_DATA)

    def test_end_to_end_workflow(self):
        # Mocking feedparser.parse to return mock RSS feed data
        with mock.patch('feedparser.parse', side_effect=self.mock_rss_feed_parse):
            # Perform the extraction
            self.extractor.extract_metadata_from_rss_feed(new_entry_count=3)

        # Check that the correct number of revisions were inserted into the revisions table
        result = self.db_interface.select(
            table="Revisions",
            columns=["revision_guid"]
        )
        self.assertEqual(
            len(result),
            3,
            "The correct number of revisions were not inserted into the revisions table"
        )
        # # Check that the correct number of bills were inserted into the bills table
        result = self.db_interface.select(
            table="Bills",
            columns=["legislative_id"]
        )
        self.assertEqual(
            len(result),
            1,
            "The correct number of bills were not inserted into the bills table"
        )
