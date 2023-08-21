from supabase import create_client, Client
import feedparser
import os
import re

from dotenv import load_dotenv
#load_dotenv() #for local secret management with .env file

senate_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml"
house_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"

sb_api_url = "https://vsumrxhpkzegrktbtcui.supabase.co"
#sb_api_key = os.getenv("SUPABASE_API_KEY") #local secret management wtih .env file
sb_api_key = os.environ["SUPABASE_API_KEY"] #github actions secret management 

def get_bill_no_from_RSS_title(title, leg_body):
    senate_bill_no_regex = '(Senate Bill \d*|Senate Resolution \d*)'
    house_bill_no_regex = '(House Bill \d*|House Resolution \d*)'
    
    if leg_body == "senate": return re.findall(senate_bill_no_regex, title)[0].split(' ')[-1]
    if leg_body == "house": return re.findall(house_bill_no_regex, title)[0].split(' ')[-1]
    return title #return the original title if legislative body not specified
    
def get_bill_printer_no_from_RSS_title(title):
    printer_no_regex="Printer's Number \d*"
    return re.findall(printer_no_regex, title)[0].split(' ')[-1]

def has_existing_supabase_records(supa_con, bill_no, printer_no, leg_body):
    existing_bill_records = supa_con.table('Revisions').select("*", count="exact").eq("bill_id", bill_no).eq("printer_no", printer_no).eq("legislative_body", leg_body).execute()
    if existing_bill_records.count > 0: return True
    else: return False

def extract_and_upload_senate_bill_metadata(supa_con):
    sen_rss = feedparser.parse(senate_rss_feed)
    
    #create an object that holds all existing house bill records in a variable/in memory
    #compare against that instead of using the has_existing supabase_records method

    for bill in sen_rss.entries:
        if bill is None: continue

        bill_no = get_bill_no_from_RSS_title(bill.title, "senate")
        printer_no = get_bill_printer_no_from_RSS_title(bill.title)

        if has_existing_supabase_records(supa_con, bill_no, printer_no, "senate"): continue
        supa_con.table('Revisions').insert(
            {
                "bill_id": bill_no,
                "printer_no": printer_no, 
                "full_text_link": bill["link"], 
                "publication_date": bill["published"], 
                "legislative_body": "senate"
                # "active_summary_id": metadata["active_summary_id"], #leaving out foreign keys for now
            }).execute()
    return

def extract_and_upload_house_bill_metadata(supa_con):
    house_rss = feedparser.parse(house_rss_feed)
    for bill in house_rss.entries:
        if bill is None: continue

        bill_no = get_bill_no_from_RSS_title(bill.title, "house")
        printer_no = get_bill_printer_no_from_RSS_title(bill.title)

        if has_existing_supabase_records(supa_con, bill_no, printer_no, "house"): continue
        supa_con.table('Revisions').insert(
            {
                "bill_id": bill_no,
                "printer_no": printer_no, 
                "full_text_link": bill["link"], 
                "publication_date": bill["published"], 
                "legislative_body": "house"
                # "active_summary_id": metadata["active_summary_id"],  #leaving out foreign keys for now
            }).execute()
    return

if __name__ == "__main__":
    supabase_connection: Client = create_client(sb_api_url, sb_api_key)
    extract_and_upload_senate_bill_metadata(supabase_connection)
    extract_and_upload_house_bill_metadata(supabase_connection)