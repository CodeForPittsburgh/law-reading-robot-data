#this program will eventually be responsible for grabbing bill metadata and full bill text to supabase

from docx import Document
from supabase import create_client, Client
from datetime import datetime
import feedparser

senate_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml"
house_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"

#what should I do with the api key (shouldn't it be a secret or something)
sb_api_url = "https://vsumrxhpkzegrktbtcui.supabase.co"
sb_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZzdW1yeGhwa3plZ3JrdGJ0Y3VpIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODQ3OTU2NzUsImV4cCI6MjAwMDM3MTY3NX0.9lafalZT9FJW1D8DAuIMrsRX0Gs6204nV8ETfGslrqI"

#on each post, check if the revision is already in the table (so you don't upload duplicates)
def extract_and_upload_senate_bill_metadata(): #research how to extract rss metadata and what rss is 
    sen_rss = feedparser.parse(senate_rss_feed)
    supabase: Client = create_client(sb_api_url, sb_api_key)

    for bill in sen_rss.entries:
        # if exists
        if bill is None: return

        title_elements = bill.title.split(' ')
        #change if bill["parss_enacted"] == "YES" and title_elements[1] == "Bill": #make sure the bill was enacted and it's a bill instead of a resolution
            
        bill_no = title_elements[2]
        printer_no = title_elements[5]

        bill_record = supabase.table('Revisions').select("*", count="exact").eq("bill_id", bill_no).eq("printer_no", printer_no).execute()
        if bill_record.count == 0: #if the bill hasn't already been posted to the table, then post it
            response = supabase.table('Revisions').upsert( #why is there no python docs for upsert?
                {
                    # "created_at": metadata["created_at"],
                    "bill_id": bill_no,
                    "printer_no": printer_no, 
                    "full_text_link": bill["link"], 
                    "publication_date": bill["published"], 
                    "legislative_body": "senate"
                    # "active_summary_id": metadata["active_summary_id"], 
                }).execute()
    return

def extract_and_upload_house_bill_metadata(): #research how to extract rss metadata and what rss is 
    house_rss = feedparser.parse(house_rss_feed)
    supabase: Client = create_client(sb_api_url, sb_api_key)

    for bill in house_rss.entries:
        # if exists
        if bill is None: return

        title_elements = bill.title.split(' ')
        #if bill["parss_enacted"] == "YES" and title_elements[1] == "Bill": #make sure the bill was enacted and it's a bill instead of a resolution
            
        bill_no = title_elements[2]
        printer_no = title_elements[5]

        bill_record = supabase.table('Revisions').select("*", count="exact").eq("bill_id", bill_no).eq("printer_no", printer_no).execute()
        if bill_record.count == 0: #if the bill hasn't already been posted to the table, then post it
            response = supabase.table('Revisions').upsert( #why is there no python docs for upsert?
                {
                    # "created_at": metadata["created_at"],
                    "bill_id": bill_no,
                    "printer_no": printer_no, 
                    "full_text_link": bill["link"], 
                    "publication_date": bill["published"], 
                    "legislative_body": "house"
                    # "active_summary_id": metadata["active_summary_id"], 
                }).execute()
    return

#extract_law_text(path)
# input: filepath of docx file
# output: a string of the law body text
def extract_law_text(path):
    output_text = ""
    doc = Document(path)

    for para in doc.paragraphs:
        for run in para.runs: #not sure what runs are, but these for loops seem to look through on a character by character basis (testing by strikethroughing a single character and this picks it up as an individual run)
            if not run.font.strike: #only extract text that isn't strikethrough 
                output_text += run.text
        output_text += ' ' #resolves spacing issues
    return output_text

#find a way to determine when the actual bill text starts
#do I need to validate that it's a docx file

def upload_to_supabase(metadata, law_text):
#connect to and post to a test supabase table
    supabase: Client = create_client(sb_api_url, sb_api_key)

    #supabase 2 part update or insert (1 for metadata and the other for the text?)

    response = supabase.table('Revisions').upsert( #why is there no python docs for upsert?
        {
            "created_at": metadata["created_at"],
            "bill_id": metadata["bill_id"],
            "printer_no": metadata["printer_no"], 
            "full_text_link": metadata["full_text_link"], 
            "publication_date": metadata["publication_date"], 
            # "active_summary_id": metadata["active_summary_id"], 
            "full_text": law_text
        }).execute()
    # print(response.data[0])
    return




#upload_to_supabase("", extract_law_text('./eg-doc-106.docx'))

# print(extract_law_text('./eg-doc-106.docx'))
# print()
# print(extract_law_text('./HB-366.docx'))

#extract_and_upload_senate_bill_metadata()
#extract_and_upload_house_bill_metadata()