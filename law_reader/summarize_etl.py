from supabase import create_client, Client
import os

"""
File for downloading full text of bills from Supabase, summarizing them, and uploading the summaries to Supabase

Pulls data from:
- Revisions
- Revision_Text

The database tables updated by this script are:
- Summaries
"""


sb_api_url = os.environ["SUPABASE_API_URL"]  # github actions secret management
sb_api_key = os.environ["SUPABASE_API_KEY"]  # github actions secret management



def get_revisions_without_summaries(supabase_connection: Client) -> list:
    """
    Pulls all revisions from Supabase that do not have a summary
    :param supabase_connection: a Supabase connection object
    :return: a list of revisions without summaries
    """
    api_response = supabase_connection.table("Revisions").select("*", count="exact").is_null("active_summary_id").execute()
    # TODO: Figure out how to get the result as a list
    # return api_response.data


def download_bill_text(supabase_connection: Client, revision_guid: str) -> str:
    """
    Downloads the full text of a bill from Supabase
    :param supabase_connection: a Supabase connection object
    :param revision_guid: the guid of the bill revision
    :return: the full text of the bill
    """
    api_response = supabase_connection.table("Revision_Text").select("full_text").eq("revision_guid", revision_guid).execute()
    return api_response.data[0]["full_text"]


def summarize_bill(bill_text: str) -> str:
    """
    A placeholder function for summarizing a bill
    :param bill_text: the text of the bill
    :return: the summary of the bill
    """
    return bill_text



def upload_summary(supabase_connection: Client, summary: str, revision_guid: str):
    """
    Uploads a summary to Supabase, linking it to the appropriate entry in the "Revisions" table
    :param supabase_connection: a Supabase connection object
    :param summary: the summary of the bill
    :param revision_guid: the guid of the bill revision
    """
    # Insert summary into Summaries table and retrieve the summary_id of the new entry
    api_response = supabase_connection.table("Summaries").insert({"summary": summary}).execute()
    summary_id = api_response.data[0]["summary_id"]
    # Update relevant entry in Revisions table (found with revision guid) with summary_id of new entry in Summaries table
    supabase_connection.table("Revisions").update({"active_summary_id": summary_id}).eq("revision_guid", revision_guid).execute()


def summarize_all_unsummarized_revisions(supabase_connection: Client):
    """
    Downloads the full text of all bills without summaries from Supabase, summarizes them, and uploads the summaries to Supabase
    :param supabase_connection: a Supabase connection object
    """
    revisions_without_summaries = get_revisions_without_summaries(supabase_connection)
    for revision in revisions_without_summaries:
        bill_text = download_bill_text(supabase_connection, revision["revision_guid"])
        summary = summarize_bill(bill_text)
        upload_summary(supabase_connection, summary, revision["revision_guid"])


if __name__ == "__main__":
    supabase_connection: Client = create_client(sb_api_url, sb_api_key)
    summarize_all_unsummarized_revisions(supabase_connection)
