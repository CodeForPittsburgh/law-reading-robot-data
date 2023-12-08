import unittest
from unittest.mock import MagicMock, patch

from law_reader.common.RevisionSummaryInfo import RevisionSummaryInfo
from law_reader.db_interfaces import DBInterface
from law_reader.summarize_etl import summarize_all_unsummarized_revisions

from law_reader.summarizer.InvalidRTUniqueIDException import InvalidRTUniqueIDException
from law_reader.summarizer.SummarizationException import SummarizationException

mock_revisions_data = [
    {"revision_guid": "guid1", "rt_unique_id": 1, "revision_internal_id": 101},
    {"revision_guid": "guid2", "rt_unique_id": 2, "revision_internal_id": 102}
    # Add more mock entries as needed
]



class TestSummarizeAllUnsummarizedRevisions(unittest.TestCase):

    def setUp(self):
        # Mock all the functions used in summarize_all_unsummarized_revisions
        db_interface_path = 'law_reader.db_interfaces.DBInterface'
        self.mock_summarize_bill = patch('law_reader.summarize_etl.summarize_bill').start()
        self.mock_summarize_bill.return_value = "Summary text"


        # Add clean up to stop the patches after each test
        self.addCleanup(patch.stopall)

        # Patch RevisionSummaryInfo
        self.mock_revision_info = MagicMock(spec=RevisionSummaryInfo)
        self.mock_revision_info.rt_unique_id = 1

        # Create a mock DB interface
        self.mock_db_interface = MagicMock(spec=DBInterface)
        self.mock_db_interface.download_bill_text.return_value = "Full bill text"

    def test_with_revisions(self):
        """
        Tests that the function calls the correct functions the correct number of times
        """
        # Configure the mocks
        mock_revisions = [self.mock_revision_info, self.mock_revision_info]

        mdi = self.mock_db_interface
        mdi.get_revisions_without_summaries.return_value = mock_revisions

        # Call the function with the mock client
        summarize_all_unsummarized_revisions(self.mock_db_interface)

        # Assertions
        mdi.get_revisions_without_summaries.assert_called_once()
        for methods in [mdi.download_bill_text, mdi.upload_summary, self.mock_summarize_bill]:
            self.assertEqual(
                methods.call_count,
                len(mock_revisions),
                msg=f"Expected {methods} to be called {len(mock_revisions)} times, but was called {methods.call_count} times")

    def test_no_revisions(self):
        """
        Tests that the function does not call any functions except for get_revisions_without_summaries
        when there are no revisions
        """
        mdi = self.mock_db_interface
        mdi.get_revisions_without_summaries.return_value = []

        summarize_all_unsummarized_revisions(self.mock_db_interface)

        mdi.get_revisions_without_summaries.assert_called_once()
        for methods in [mdi.download_bill_text, mdi.upload_summary, self.mock_summarize_bill]:
            methods.assert_not_called()

    def test_summarization_error_handling(self):
        """
        Tests that the function does not call upload_summary if the summarization fails
        """
        self.mock_db_interface.get_revisions_without_summaries.return_value = [self.mock_revision_info]
        self.mock_summarize_bill.side_effect = SummarizationException("Error")

        summarize_all_unsummarized_revisions(self.mock_db_interface)

        self.mock_summarize_bill.assert_called_once()
        self.mock_db_interface.upload_summary.assert_not_called()

    def test_download_bill_text_error_handling(self):
        """
        Tests that the function does not call summarize_bill or upload_summary if the download fails
        """
        mdi = self.mock_db_interface
        mdi.get_revisions_without_summaries.return_value = [self.mock_revision_info]
        mdi.download_bill_text.side_effect = InvalidRTUniqueIDException("Error")

        summarize_all_unsummarized_revisions(self.mock_db_interface)

        mdi.download_bill_text.assert_called_once()
        self.mock_summarize_bill.assert_not_called()
        mdi.upload_summary.assert_not_called()

