from docx import Document
from supabase import create_client, Client
import os
import subprocess
import requests

#from dotenv import load_dotenv
#load_dotenv() #for local secret management with .env file

senate_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml"
house_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"

sb_api_url = "https://vsumrxhpkzegrktbtcui.supabase.co"
#sb_api_key = os.getenv("SUPABASE_API_KEY") #local secret management wtih .env file
sb_api_key = os.environ["SUPABASE_API_KEY"] #github actions secret management 

def dowload_bill_doc_file(bill_link):
    bill_link = bill_link.replace("txtType=HTM", "txtType=DOC") #change link to doc download
    response = requests.get(bill_link, stream=True)
    output_file_name = "bill.doc"
    with open(output_file_name, "wb") as f: #add try catch here and return empty filname if it fails
        f.write(response.content)
    return output_file_name

def convert_doc_to_docx(bill_path):
    new_file_name = ""
    try:
        subprocess.call(['libreoffice', '--headless', '--convert-to', 'docx', bill_path])
        new_file_name = bill_path.replace(".doc", ".docx")
    except FileNotFoundError:
        raise FileNotFoundError(f"The file could not be found.")
    return new_file_name

def extract_law_text_from_docx(bill_path):
    output_text = ""
    doc = Document(bill_path)

    #update to only include docs that haven't been posted yet
    # find a way to determine when the actual bill text starts

    for para in doc.paragraphs:
        for run in para.runs: #not sure what runs are, but these for loops seem to look through on a character by character basis (testing by strikethroughing a single character and this picks it up as an individual run)
            if not run.font.strike: #only extract text that isn't strikethrough 
                output_text += run.text
        output_text += ' ' #resolves spacing issues
    return output_text

def extract_and_upload_missing_bill_text(supa_con):
    bill_records_missing_text = supa_con.table("Revisions").select("*").filter("full_text", "is", "null").execute()
    for record in bill_records_missing_text.data:
        bill_path = dowload_bill_doc_file(record["full_text_link"])
        bill_docx_path = convert_doc_to_docx(bill_path)
        bill_text = extract_law_text_from_docx(bill_docx_path)
        os.remove(bill_path)
        os.remove(bill_docx_path)
        supa_con.table('Revisions').update({ "full_text": bill_text }).eq("bill_id", record["bill_id"]).eq("printer_no", record["printer_no"]).eq("legislative_body", record["legislative_body"]).eq("full_text_link", record["full_text_link"]).execute()
    return

if __name__ == "__main__":
    supabase_connection: Client = create_client(sb_api_url, sb_api_key)
    extract_and_upload_missing_bill_text(supabase_connection)