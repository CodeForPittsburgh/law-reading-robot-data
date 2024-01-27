from typing import Optional

from docx import Document
import os
import subprocess
import requests

from law_reader.db_interfaces.PostgresDBInterface import PostgresDBInterface
from law_reader import DBInterface


def make_temp_if_not_exists():
    """
    Creates a temp directory if it does not already exist
    """
    if not os.path.exists("temp"):
        os.mkdir("temp")

def download_bill_doc_file(bill_link: str) -> Optional[str]:
    """
    Downloads a .doc file from a given link
    :param bill_link: link to the .doc file
    :return: path to the downloaded .doc file
    """
    bill_link = bill_link.replace("txtType=HTM", "txtType=DOC")  # change link to doc download
    # TODO: Should I add more precise logging here? Will Github Actions report the timestamp of print statements?
    print(f"Downloading bill at {bill_link}")
    response = requests.get(bill_link, stream=True)
    print("Writing bill to file")
    make_temp_if_not_exists()
    output_file_path = "temp/bill.doc"
    with open(output_file_path, "wb") as f:
        f.write(response.content)
    print("Finished writing bill to file")
    return output_file_path


def convert_doc_to_docx(bill_path: str) -> str:
    """
    Converts a .doc file to a .docx file using LibreOffice
    :param bill_path: path to the .doc file
    :return: path to the .docx file
    """
    print("Attempting to convert file to docx...")
    try:
        subprocess.call(['libreoffice', '--headless', '--convert-to', 'docx:MS Word 2007 XML', bill_path, '--outdir', "temp"])
        print("Conversion successful.")
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
        output_text += ' \n'  # resolves spacing issues
    return output_text


def extract_and_upload_missing_bill_text(db_interface: DBInterface):
    """
    Extracts the law text from a .docx file and uploads it to Supabase
    :param db_interface: a DBInterface object
    """
    # TODO: Modify so that this might also pull records which have not had a summary prior to a certain date
    bill_records_missing_text = db_interface.get_revisions_without_bill_text()
    for revision in bill_records_missing_text:
        bill_path = download_bill_doc_file(revision.full_text_link)
        bill_docx_path = convert_doc_to_docx(bill_path)
        bill_text = extract_law_text_from_docx(bill_docx_path)
        os.remove(bill_path)
        os.remove(bill_docx_path)
        db_interface.upload_bill_text(bill_text, revision.revision_guid)
    db_interface.commit()

if __name__ == "__main__":
    extract_and_upload_missing_bill_text(db_interface=PostgresDBInterface())
