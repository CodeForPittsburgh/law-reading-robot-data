from unittest.mock import MagicMock
from law_reader import Extractor, SupabaseDBInterface


# TODO: Rewrite as unit tests after refactor
class TestExtractor:

    def setUp(self) -> None:
        pass

    def print_call_output_dict(self, call_args_list):
        for idx, call in enumerate(call_args_list):
            print(f"{idx}: Insert to {call[0][0].table_name}: {call[0][0].output_dict}")

    def test_extract_metadata_from_rss_feed(self):
        rss_extractor = Extractor(
            db_interface=SupabaseDBInterface(),
            chamber="House",
            rss_feed="https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"
        )
        rss_extractor.insert_new_record = MagicMock()
        rss_extractor.extract_metadata_from_rss_feed()

        # Print out the mock call arguments
        self.print_call_output_dict(rss_extractor.insert_new_record.call_args_list)


