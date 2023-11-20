import unittest
from unittest.mock import MagicMock, patch

import postgrest

from common.RevisionSummaryInfo import RevisionSummaryInfo
from summarize_etl import get_revisions_without_summaries, download_bill_text, summarize_bill, upload_summary, summarize_all_unsummarized_revisions
from supabase import Client, create_client

from summarizer.InvalidRTUniqueIDException import InvalidRTUniqueIDException
from summarizer.SummarizationException import SummarizationException

mock_revisions_data = [
    {"revision_guid": "guid1", "rt_unique_id": 1, "revision_internal_id": 101},
    {"revision_guid": "guid2", "rt_unique_id": 2, "revision_internal_id": 102}
    # Add more mock entries as needed
]




class TestGetRevisionsWithoutSummaries(unittest.TestCase):

    def setUp(self):
        # Mock the Client constructor
        patcher = patch('supabase.Client.__init__', return_value=None)
        self.mock_init = patcher.start()
        self.addCleanup(patcher.stop)

        # Create a mock Client object
        self.mock_client = Client(None, None)

        # Mock the table method
        patcher = patch('supabase.Client.table')
        self.mock_table = patcher.start()
        self.addCleanup(patcher.stop)




    def test_non_empty_response(self):
        """
        Test that the function returns the correct number of results
        and that the results contain the correct information
        """
        # Configure the mock for the table method
        self.mock_table.return_value.select.return_value.is_.return_value.execute.return_value = MagicMock(data=mock_revisions_data)

        # Call the function with the mock client
        results = get_revisions_without_summaries(self.mock_client)

        # Assertions
        self.assertEqual(len(results), len(mock_revisions_data))
        self.assertEqual(results[0].revision_guid, "guid1")

    def test_empty_response(self):
        """
        Test that the function returns an empty list when the API call returns no results
        """
        # Configure the mock for the table method to return an empty list
        self.mock_table.return_value.select.return_value.is_.return_value.execute.return_value = MagicMock(data=[])

        # Call the function with the mock client
        results = get_revisions_without_summaries(self.mock_client)

        # Assertions
        self.assertEqual(len(results), 0)

    def test_api_error_handling(self):
        # Mock the chained methods
        mock_execute = self.mock_client.table("Revisions").select("*").is_("active_summary_id", "NULL")
        mock_execute.execute = MagicMock(side_effect=Exception("API Error"))

        # Verify that the function raises an exception when the API call fails
        with self.assertRaises(Exception):
            get_revisions_without_summaries(self.mock_client)

class TestSummarizeAllUnsummarizedRevisions(unittest.TestCase):

    def setUp(self):
        # Mock all the functions used in summarize_all_unsummarized_revisions
        self.mock_get_revisions_without_summaries = patch('summarize_etl.get_revisions_without_summaries').start()
        self.mock_download_bill_text = patch('summarize_etl.download_bill_text').start()
        self.mock_summarize_bill = patch('summarize_etl.summarize_bill').start()
        self.mock_upload = patch('summarize_etl.upload_summary').start()

        # Add clean up to stop the patches after each test
        self.addCleanup(patch.stopall)

        # Patch RevisionSummaryInfo
        self.mock_revision_info = MagicMock(spec=RevisionSummaryInfo)
        self.mock_revision_info.rt_unique_id = 1



        # Mock the Client constructor
        patcher = patch('supabase.Client.__init__', return_value=None)
        self.mock_init = patcher.start()
        self.addCleanup(patcher.stop)

        # Create a mock Client object
        self.mock_client = Client(None, None)

    def test_with_revisions(self):
        """
        Tests that the function calls the correct functions the correct number of times
        """
        # Configure the mocks
        self.mock_download_bill_text.return_value = "Full bill text"
        self.mock_summarize_bill.return_value = "Summary text"

        mock_revisions = [self.mock_revision_info, self.mock_revision_info]
        self.mock_get_revisions_without_summaries.return_value = mock_revisions

        # Call the function with the mock client
        summarize_all_unsummarized_revisions(self.mock_client)

        # Assertions
        self.mock_get_revisions_without_summaries.assert_called_once()
        self.assertEqual(self.mock_download_bill_text.call_count, len(mock_revisions))
        self.assertEqual(self.mock_summarize_bill.call_count, len(mock_revisions))
        self.assertEqual(self.mock_upload.call_count, len(mock_revisions))

    def test_no_revisions(self):
        """
        Tests that the function does not call any functions except for get_revisions_without_summaries
        when there are no revisions
        """
        self.mock_get_revisions_without_summaries.return_value = []

        summarize_all_unsummarized_revisions(self.mock_client)

        self.mock_get_revisions_without_summaries.assert_called_once()
        self.mock_download_bill_text.assert_not_called()
        self.mock_summarize_bill.assert_not_called()
        self.mock_upload.assert_not_called()

    def test_summarization_error_handling(self):
        """
        Tests that the function does not call upload_summary if the summarization fails
        """
        self.mock_get_revisions_without_summaries.return_value = [self.mock_revision_info]
        self.mock_download_bill_text.return_value = "Full bill text"
        self.mock_summarize_bill.side_effect = SummarizationException("Error")

        summarize_all_unsummarized_revisions(self.mock_client)

        self.mock_summarize_bill.assert_called_once()
        self.mock_upload.assert_not_called()

    def test_download_bill_text_error_handling(self):
        """
        Tests that the function does not call summarize_bill or upload_summary if the download fails
        """
        self.mock_get_revisions_without_summaries.return_value = [self.mock_revision_info]
        self.mock_download_bill_text.side_effect = InvalidRTUniqueIDException("Error")

        summarize_all_unsummarized_revisions(self.mock_client)

        self.mock_download_bill_text.assert_called_once()
        self.mock_summarize_bill.assert_not_called()
        self.mock_upload.assert_not_called()


class TestDownloadBillText(unittest.TestCase):

    def setUp(self):

        # Create a mock Client object
        self.mock_client = MagicMock(spec=Client)

        # Create a mock API response
        self.mock_api_response = MagicMock(spec=postgrest.APIResponse)

    def set_mock_api_response(self, data):
        self.mock_api_response.data = data
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = self.mock_api_response

    def test_download_bill_text(self):

        # Setup mock return values for Supabase API call
        self.set_mock_api_response([{"full_text": "Full text of the bill"}])

        # Test the function with a mock Supabase client and a dummy ID
        bill_text = download_bill_text(self.mock_client, 123)
        self.assertEqual(bill_text, "Full text of the bill")

    def test_download_bill_text_empty_api_response(self):
        """
        In the case of an empty API response, the function should raise an InvalidRTUniqueIDException
        """
        # Setup mock return values for Supabase API call
        self.set_mock_api_response([])

        # Test handling of empty API response
        with self.assertRaises(InvalidRTUniqueIDException):
            download_bill_text(self.mock_client, 123)

    def test_download_bill_text_multiple_api_responses(self):
        """
        In the case of multiple API responses, the function should raise an InvalidRTUniqueIDException
        """
        # Setup mock return values for Supabase API call
        self.set_mock_api_response([{"full_text": "Full text of the bill"}, {"full_text": "Another bill"}])

        # Test handling of multiple API responses
        with self.assertRaises(InvalidRTUniqueIDException):
            download_bill_text(self.mock_client, 123)

    def test_download_bill_text_no_text(self):
        """
        In the case of an empty API response, the function should raise an InvalidRTUniqueIDException
        """
        # Setup mock return values for Supabase API call
        self.set_mock_api_response([{"full_text": ""}])

        # Test handling of empty API response
        with self.assertRaises(InvalidRTUniqueIDException):
            download_bill_text(self.mock_client, 123)



class TestSummarizeBill(unittest.TestCase):

    @patch('summarize_etl.Summarization.__init__', return_value=None)
    @patch('summarize_etl.Summarization.get_summary')
    def test_summarize_bill(self, mock_get_summary, mock_init):
        # Setup mock return value
        mock_get_summary.return_value = "Mock Summary"

        # Test with valid input
        summary = summarize_bill("Sample bill text")
        mock_get_summary.assert_called_once_with("Sample bill text")
        self.assertEqual(summary, "Mock Summary")

        # Test with empty input
        summary = summarize_bill("")
        mock_get_summary.assert_called_with("")
        self.assertEqual(summary, "Mock Summary")

class TestUploadSummary(unittest.TestCase):

    def setUp(self) -> None:
        # Create a mock Client object
        self.mock_client = MagicMock(spec=Client)

    """
    Test successful upload
    """
    def test_upload_summary(self):
        # Mock the API response for the insert call
        self.mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"summary_id": 1}])

        # Create mock RevisionSummaryInfo object
        mock_revision_info = MagicMock(spec=RevisionSummaryInfo)
        mock_revision_info.revision_guid = "guid1"
        mock_revision_info.revision_internal_id = 101

        # Call the function with the mock client
        upload_summary(self.mock_client, mock_revision_info, "Summary text")

        # Assertions
        self.mock_client.table.return_value.insert.assert_called_once_with({"summary_text": "Summary text", "revision_internal_id": 101})
        self.mock_client.table.return_value.update.assert_called_once_with({"active_summary_id": 1})
        self.mock_client.table.return_value.update.return_value.eq.assert_called_once_with("revision_guid", "guid1")
        self.mock_client.table.return_value.update.return_value.eq.return_value.execute.assert_called_once()