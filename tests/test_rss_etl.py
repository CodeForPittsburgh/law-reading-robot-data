from unittest.mock import MagicMock
from law_reader import Extractor, sb_api_url
from supabase import create_client

# Readonly version of code for testing
sb_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZzdW1yeGhwa3plZ3JrdGJ0Y3VpIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODQ3OTU2NzUsImV4cCI6MjAwMDM3MTY3NX0.9lafalZT9FJW1D8DAuIMrsRX0Gs6204nV8ETfGslrqI"


# TODO: Rewrite as unit tests after refactor
class TestExtractor:

    def setUp(self) -> None:
        self.supabase_connection = create_client(sb_api_url, sb_api_key)

    def print_call_output_dict(self, call_args_list):
        for idx, call in enumerate(call_args_list):
            print(f"{idx}: Insert to {call[0][0].table_name}: {call[0][0].output_dict}")

    def test_extract_metadata_from_rss_feed(self):
        rss_extractor = Extractor(
            supa_con=self.supabase_connection,
            chamber="House",
            rss_feed="https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"
        )
        rss_extractor.insert_new_record = MagicMock()
        rss_extractor.extract_metadata_from_rss_feed()

        # Print out the mock call arguments
        self.print_call_output_dict(rss_extractor.insert_new_record.call_args_list)


