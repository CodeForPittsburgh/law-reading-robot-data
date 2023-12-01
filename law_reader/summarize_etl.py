from supabase import create_client, Client
import os
import argparse

from law_reader.db_interfaces import SupabaseDBInterface, DBInterface
from law_reader.common.RevisionSummaryInfo import RevisionSummaryInfo
from law_reader.summarizer.InvalidRTUniqueIDException import InvalidRTUniqueIDException
from law_reader.summarizer.SummarizationException import SummarizationException
from law_reader.summarizer.summarization import Summarization

"""
File for downloading full text of bills from Supabase, summarizing them, and uploading the summaries to Supabase

Pulls data from:
- Revisions
- Revision_Text

The database tables updated by this script are:
- Summaries
"""
def summarize_bill(bill_text: str) -> str:
    """
    A placeholder function for summarizing a bill
    :param bill_text: the text of the bill
    :return: the summary of the bill
    """
    # TODO: We currently don't have a means to account for if the LLM responds
    #  with an error message. We should add that in the future.
    summarizer = Summarization()
    return summarizer.get_summary(bill_text)

def summarize_all_unsummarized_revisions(db_interface: DBInterface):
    """
    Downloads the full text of all bills without summaries from Supabase,
    summarizes them, and uploads the summaries to Supabase
    Any bills that cannot be summarized will be skipped
    :param db_interface: Interface to the database
    """
    revisions_without_summaries: list[RevisionSummaryInfo] = db_interface.get_revisions_without_summaries()
    for revision_info in revisions_without_summaries:
        try:
            full_text = db_interface.download_bill_text(revision_info.rt_unique_id)
            summary_text = summarize_bill(full_text)
            db_interface.upload_summary(revision_info, summary_text)
        except SummarizationException:
            continue
        except InvalidRTUniqueIDException:
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize bills from Database")
    # Add a boolean argument for the debug flag
    parser.add_argument('-d', '--debug', action='store_true', help='Print debug messages')
    # Parse the arguments
    args = parser.parse_args()
    db_interface: DBInterface = SupabaseDBInterface(args.debug)

    summarize_all_unsummarized_revisions(db_interface)
