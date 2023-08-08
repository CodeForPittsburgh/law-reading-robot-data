"""

Description: this program will eventually be responsible for extracting RSS senate/house bill metadata and DOCX full bill, and then uploading to supabase table


"""

from docx import Document
from supabase import create_client, Client
from datetime import datetime
import feedparser
import os
import re

senate_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml"
house_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"

sb_api_url = "https://vsumrxhpkzegrktbtcui.supabase.co" #os.environ["API_URL"] 
sb_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZzdW1yeGhwa3plZ3JrdGJ0Y3VpIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODQ3OTU2NzUsImV4cCI6MjAwMDM3MTY3NX0.9lafalZT9FJW1D8DAuIMrsRX0Gs6204nV8ETfGslrqI" #os.environ["API_KEY"] 

def extract_and_upload_senate_bill_metadata():
    sen_rss = feedparser.parse(senate_rss_feed)
    supabase: Client = create_client(sb_api_url, sb_api_key)
    for bill in sen_rss.entries:
        #print("checking bill ", bill.title)
        if bill is None: continue

        bill_no_regex = '(Senate Bill \d*|Senate Resolution \d*)'
        bill_no = re.findall(bill_no_regex, bill.title)[0].split(' ')[-1]
        
        printer_no_regex="Printer's Number \d*"
        printer_no = re.findall(printer_no_regex, bill.title)[0].split(' ')[-1]

        #OLD CODE that doesn't work
        #title_elements = bill.title.split(' ') #grabbing bill and printer numbers from the title (not explicitly given in RSS feed)
        #bill_no = "".join(char for char in title_elements[2] if char.isdigit()) #ensuring that only the actual digits of the bill number are extracted
        #printer_no = "".join(char for char in title_elements[5] if char.isdigit()) #ensuring that only the actual digits of the printer number are extracted

        #change if bill["parss_enacted"] == "YES" and title_elements[1] == "Bill": #make sure the bill was enacted and it's a bill instead of a resolution        
        bill_existing_records = supabase.table('Revisions').select("*", count="exact").eq("bill_id", bill_no).eq("printer_no", printer_no).eq("legislative_body", "senate").execute()
        if bill_existing_records.count == 0: #if the bill hasn't already been recorded in the supabase table, then post it (so you don't upload duplicates)
            response = supabase.table('Revisions').insert( #why is there no python docs for upsert?
                {
                    # "created_at": metadata["created_at"], #supabase already defaults to now(), so this is kind of unnecessary for now
                    "bill_id": bill_no,
                    "printer_no": printer_no, 
                    "full_text_link": bill["link"], 
                    "publication_date": bill["published"], 
                    "legislative_body": "senate"
                    # "active_summary_id": metadata["active_summary_id"], #leaving out foreign keys for now
                }).execute()
            print(response)
    return

def extract_and_upload_house_bill_metadata():
    house_rss = feedparser.parse(house_rss_feed)
    supabase: Client = create_client(sb_api_url, sb_api_key)
    for bill in house_rss.entries:
        #print("checking bill ", bill.title)
        if bill is None: continue

        bill_no_regex = '(House Bill \d*|House Resolution \d*)'
        bill_no = re.findall(bill_no_regex, bill.title)[0].split(' ')[-1]

        printer_no_regex="Printer's Number \d*"
        printer_no = re.findall(printer_no_regex, bill.title)[0].split(' ')[-1]

        #old code that doesn't work
        #title_elements = bill.title.split(' ')#grabbing bill and printer numbers from the title (not explicitly given in RSS feed)
        #bill_no = "".join(char for char in title_elements[2] if char.isdigit()) #ensuring that only the actual digits of the bill number are extracted
        #printer_no = "".join(char for char in title_elements[5] if char.isdigit()) #ensuring that only the actual digits of the printer number are extracted

        #if bill["parss_enacted"] == "YES" and title_elements[1] == "Bill": #make sure the bill was enacted and it's a bill instead of a resolution
        bill_record = supabase.table('Revisions').select("*", count="exact").eq("bill_id", bill_no).eq("printer_no", printer_no).eq("legislative_body", "house").execute()
        if bill_record.count == 0: #if the bill hasn't already been recorded in the supabase table, then post it (so you don't upload duplicates)
            response = supabase.table('Revisions').insert( #why is there no python docs for upsert?
                {
                    # "created_at": metadata["created_at"], #supabase already defaults to now(), so this is kind of unnecessary for now
                    "bill_id": bill_no,
                    "printer_no": printer_no, 
                    "full_text_link": bill["link"], 
                    "publication_date": bill["published"], 
                    "legislative_body": "house"
                    # "active_summary_id": metadata["active_summary_id"], # "active_summary_id": metadata["active_summary_id"], #leaving out foreign keys for now
                }).execute()
    return

#
# THE COMMENTED OUT CODE BELOW WORKS, but is on hold until the doc to docx conversion process has been implemented
#

"""
looked into temorarily storing in vm, then manipulating files within an actions runner
you can save to the home directory as shown here: https://medium.com/@fonseka.live/sharing-data-in-github-actions-a9841a9a6f42
how this is actually implemented will dramatically impact how my extract law text function works
"""

def extract_law_text(filepath):
    # output_text = ""
    # doc = Document(filepath)

    # #update to only include docs that haven't been posted yet
    #find a way to determine when the actual bill text starts
    #do I need to validate that it's a docx file


    # for para in doc.paragraphs:
    #     for run in para.runs: #not sure what runs are, but these for loops seem to look through on a character by character basis (testing by strikethroughing a single character and this picks it up as an individual run)
    #         if not run.font.strike: #only extract text that isn't strikethrough 
    #             output_text += run.text
    #     output_text += ' ' #resolves spacing issues
    # return output_text
    return

def process_docx_files(): #function to handle the scraping and uploading of all docx files
    # get all bills from revsions withe empty full_text fields
    # for each bill, post
    return


if __name__ == "__main__":
    extract_and_upload_senate_bill_metadata()
    extract_and_upload_house_bill_metadata()
    #include text extraction logic later