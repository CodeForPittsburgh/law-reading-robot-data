from supabase import create_client, Client
import os

from common.RevisionSummaryInfo import RevisionSummaryInfo

"""
File for downloading full text of bills from Supabase, summarizing them, and uploading the summaries to Supabase

Pulls data from:
- Revisions
- Revision_Text

The database tables updated by this script are:
- Summaries
"""

DEBUG = True  # Set to True to print debug messages
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
sb_api_url = os.environ["SUPABASE_API_URL"]  # github actions secret management
sb_api_key = os.environ["SUPABASE_API_KEY"]  # github actions secret management


def get_revisions_without_summaries(supabase_connection: Client) -> list[RevisionSummaryInfo]:
    """
    Pulls all revisions from Supabase that do not have a summary
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
    return "This is a placeholder summary."


def download_bill_text(supabase_connection: Client, rt_unique_id: int) -> str:
    """
    Downloads the full text of a bill from Supabase
    :param supabase_connection: a Supabase connection object
    :param rt_unique_id: the unique id of the bill in the Revision_Text table
    :return: the full text of the bill
    """
    api_response = supabase_connection.table("Revision_Text").select("full_text").eq("rt_unique_id", rt_unique_id).execute()
    return api_response.data[0]["full_text"]

def upload_summary(supabase_connection: Client, revision_info: RevisionSummaryInfo):
    """
    Uploads a summary to Supabase, linking it to the appropriate entry in the "Revisions" table
    :param supabase_connection: a Supabase connection object
    :param summary: the summary of the bill
    :param revision_guid: the guid of the bill revision
    """
    # Insert summary into Summaries table and retrieve the summary_id of the new entry
    api_response = supabase_connection.table("Summaries").insert(
        {"summary_text": revision_info.summary,
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
    Downloads the full text of all bills without summaries from Supabase, summarizes them, and uploads the summaries to Supabase
    :param supabase_connection: a Supabase connection object
    """
    revisions_without_summaries = get_revisions_without_summaries(supabase_connection)
    for revision_info in revisions_without_summaries:
        revision_info.full_text = download_bill_text(supabase_connection, revision_info.rt_unique_id)
        revision_info.summary = summarize_bill(revision_info.full_text)
        upload_summary(supabase_connection, revision_info)


if __name__ == "__main__":
    supabase_connection: Client = create_client(sb_api_url, sb_api_key)
    summarize_all_unsummarized_revisions(supabase_connection)
