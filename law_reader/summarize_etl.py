from supabase import create_client, Client
import os
import argparse

from common.RevisionSummaryInfo import RevisionSummaryInfo
from summarizer.InvalidRTUniqueIDException import InvalidRTUniqueIDException
from summarizer.SummarizationException import SummarizationException
from summarizer.summarization import Summarization

"""
File for downloading full text of bills from Supabase, summarizing them, and uploading the summaries to Supabase

Pulls data from:
- Revisions
- Revision_Text

The database tables updated by this script are:
- Summaries
"""
def get_revisions_without_summaries(supabase_connection: Client) -> list[RevisionSummaryInfo]:
    """
    Pulls all revisions from Supabase that do not have a summary
    A revision is considered to have a summary if its active_summary_id column in the REVISIONS table is not NULL
    :param supabase_connection: a Supabase connection object
    :return: a list of revisions without summaries
    """
    api_response = supabase_connection.table("Revisions").select("*", count="exact").is_("active_summary_id", "NULL").execute()
    # Put relevant information from each entry into a RevisionTextInfo object
    results = [RevisionSummaryInfo(entry["revision_guid"], entry["rt_unique_id"], entry["revision_internal_id"]) for entry in api_response.data]
    return results

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


def download_bill_text(supabase_connection: Client, rt_unique_id: int) -> str:
    """
    Downloads the full text of a bill from Supabase, using the rt_unique_id
    Raises an InvalidRTUniqueIDException if the bill cannot be found
     or if multiple bills are found with the given rt_unique_id
    :param supabase_connection: a Supabase connection object
    :param rt_unique_id: the unique id of the bill in the Revision_Text table
    :return: the full text of the bill
    """
    api_response = supabase_connection.table("Revision_Text").select("full_text").eq("rt_unique_id", rt_unique_id).execute()
    if len(api_response.data) == 0:
        raise InvalidRTUniqueIDException(f"Could not find bill with rt_unique_id {rt_unique_id}")
    elif len(api_response.data) > 1:
        raise InvalidRTUniqueIDException(f"Found multiple bills with rt_unique_id {rt_unique_id}")
    text = api_response.data[0]["full_text"]
    if text is None or text == "":
        raise InvalidRTUniqueIDException(f"Bill with rt_unique_id {rt_unique_id} has no text")
    return text

def upload_summary(supabase_connection: Client, revision_info: RevisionSummaryInfo, summary_text: str):
    """
    Uploads a summary to Supabase, linking it to the appropriate entry in the "Revisions" table
    :param supabase_connection: a Supabase connection object
    :param revision_info: a RevisionSummaryInfo object containing information about the revision
    :param summary_text: the text of the summary
    """
    # Insert summary into Summaries table and retrieve the summary_id of the new entry
    api_response = supabase_connection.table("Summaries").insert(
        {"summary_text": summary_text,
         "revision_internal_id": revision_info.revision_internal_id}).\
        execute()
    summary_id = api_response.data[0]["summary_id"]
    # Update relevant entry in Revisions table (found with revision guid) with summary_id of new entry in Summaries table
    supabase_connection.table("Revisions").\
        update({"active_summary_id": summary_id}).\
        eq("revision_guid", revision_info.revision_guid).\
        execute()


def summarize_all_unsummarized_revisions(supabase_connection: Client):
    """
    Downloads the full text of all bills without summaries from Supabase,
    summarizes them, and uploads the summaries to Supabase
    Any bills that cannot be summarized will be skipped
    :param supabase_connection: a Supabase connection object
    """
    revisions_without_summaries = get_revisions_without_summaries(supabase_connection)
    for revision_info in revisions_without_summaries:
        try:
            full_text = download_bill_text(supabase_connection, revision_info.rt_unique_id)
            summary_text = summarize_bill(full_text)
            upload_summary(supabase_connection, revision_info, summary_text)
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

    # if debug flag is set, pull data from .env file
    # In production, the environment variables will be set in the github actions workflow
    if args.debug:
        from dotenv import load_dotenv
        load_dotenv()  # Load environment variables from .env file
    sb_api_url = os.environ["SUPABASE_API_URL"]  # github actions secret management
    sb_api_key = os.environ["SUPABASE_API_KEY"]  # github actions secret management

    supabase_connection: Client = create_client(sb_api_url, sb_api_key)
    summarize_all_unsummarized_revisions(supabase_connection)
