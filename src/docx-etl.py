from docx import Document
from supabase import create_client, Client
import os
import subprocess
import requests

# TODO: This code is identical to the code of my latest draft in src\rss-etl.py. Consider refactoring to avoid duplication.
DEBUG = True  # Set to True to print debug messages
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
sb_api_url = os.environ["SUPABASE_API_URL"]  # github actions secret management
sb_api_key = os.environ["SUPABASE_API_KEY"]  # github actions secret management


def download_bill_doc_file(bill_link: str) -> str:
    """
    Downloads a .doc file from a given link
    :param bill_link: link to the .doc file
    :return: path to the downloaded .doc file
    """
    bill_link = bill_link.replace("txtType=HTM", "txtType=DOC")  # change link to doc download
    response = requests.get(bill_link, stream=True)
    output_file_name = "bill.doc"
    with open(output_file_name, "wb") as f:  # add try catch here and return empty filename if it fails
        f.write(response.content)
    return output_file_name


def convert_doc_to_docx(bill_path: str) -> str:
    """
    Converts a .doc file to a .docx file using LibreOffice
    :param bill_path: path to the .doc file
    :return: path to the .docx file
    """
    try:
        subprocess.call(['libreoffice', '--headless', '--convert-to', 'docx', bill_path])
        return bill_path.replace(".doc", ".docx")
    except FileNotFoundError:
        raise FileNotFoundError(f"The file could not be found.")


def extract_law_text_from_docx(bill_path: str) -> str:
    """
    Extracts the law text from a .docx file
    :param bill_path: path to the .docx file
    :return: extracted law text
    """

    # TODO: update to only include docs that haven't been posted yet
    # TODO: find a way to determine when the actual bill text starts
    doc = Document(bill_path)
    output_text = ""
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:  # not sure what runs are, but these for loops seem to look through on a character by character basis (testing by strikethroughing a single character and this picks it up as an individual run)
            if not run.font.strike:  # only extract text that isn't strikethrough
                output_text += run.text
        output_text += ' '  # resolves spacing issues
    return output_text


def extract_and_upload_missing_bill_text(supa_con: Client):
    """
    Extracts the law text from a .docx file and uploads it to Supabase
    :param supa_con: Supabase connection object
    """
    # TODO: Modify so that this might also pull records which have not had a summary prior to a certain date
    bill_records_missing_text = supa_con.table("Revisions").select("*").filter("full_text", "is", "null").execute()
    for record in bill_records_missing_text.data:
        bill_path = download_bill_doc_file(record["full_text_link"])
        bill_docx_path = convert_doc_to_docx(bill_path)
        bill_text = extract_law_text_from_docx(bill_docx_path)
        os.remove(bill_path)
        os.remove(bill_docx_path)
        upload_bill_text(supa_con, bill_text, record["revision_guid"])


def upload_bill_text(supa_con: Client, full_text: str, revision_guid: str):
    """
    Uploads the law text from a .docx file to Supabase's "Revision_Text" table,
    linking it to the appropriate entry in the "Revisions" table
    :param supa_con: Supabase connection object
    :param full_text: full text of the bill revision
    :param revision_guid: guid of the bill revision
    """

    # Insert full text as entry in Revision_Text table, retrieving the rt_unique_id of the new entry
    # TODO: Check that this function returns the rt_unique_id of the new entry
    rt_unique_id = supa_con.table('Revision_Text').insert({"full_text": full_text}).execute()

    # Update relevant entry in Revisions table (found with revision guid) with rt_unique_id of  new entry in Revision_Text table
    supa_con.table('Revisions').update({"rt_unique_id": rt_unique_id}).eq("revision_guid", revision_guid).execute()


if __name__ == "__main__":
    supabase_connection: Client = create_client(sb_api_url, sb_api_key)
    extract_and_upload_missing_bill_text(supabase_connection)
