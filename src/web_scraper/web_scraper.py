#
# antiquated code
#

# """
# Description: this program will eventually be responsible for extracting RSS senate/house bill metadata and DOCX full bill, and then uploading to supabase table
# """

# from docx import Document
# from supabase import create_client, Client
# from datetime import datetime
# import feedparser
# import os
# import re
# import subprocess
# import requests

# from dotenv import load_dotenv
# #load_dotenv() #for local secret management with .env file

# senate_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml"
# house_rss_feed = "https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml"

# sb_api_url = "https://vsumrxhpkzegrktbtcui.supabase.co"
# #sb_api_key = os.getenv("SUPABASE_API_KEY") #local secret management wtih .env file
# sb_api_key = os.environ["SUPABASE_API_KEY"] #github actions secret management 

# def get_bill_no_from_RSS_title(title, leg_body):
#     senate_bill_no_regex = '(Senate Bill \d*|Senate Resolution \d*)'
#     house_bill_no_regex = '(House Bill \d*|House Resolution \d*)'
    
#     if leg_body == "senate": return re.findall(senate_bill_no_regex, title)[0].split(' ')[-1]
#     if leg_body == "house": return re.findall(house_bill_no_regex, title)[0].split(' ')[-1]
#     return title #return the original title if legislative body not specified
    
# def get_bill_printer_no_from_RSS_title(title):
#     printer_no_regex="Printer's Number \d*"
#     return re.findall(printer_no_regex, title)[0].split(' ')[-1]

# def has_existing_supabase_records(supa_con, bill_no, printer_no, leg_body):
#     existing_bill_records = supa_con.table('Revisions').select("*", count="exact").eq("bill_id", bill_no).eq("printer_no", printer_no).eq("legislative_body", leg_body).execute()
#     if existing_bill_records.count > 0: return True
#     else: return False

# def dowload_bill_doc_file(bill_link):
#     bill_link = bill_link.replace("txtType=HTM", "txtType=DOC") #change link to doc download
#     response = requests.get(bill_link, stream=True)
#     output_file_name = "bill.doc"
#     with open(output_file_name, "wb") as f:
#         f.write(response.content)
#     return output_file_name

# def convert_doc_to_docx(bill_path):
#     new_file_name = ""
#     try:
#         subprocess.call(['libreoffice', '--headless', '--convert-to', 'docx', bill_path])
#         new_file_name = bill_path.replace(".doc", ".docx")
#     except FileNotFoundError:
#         raise FileNotFoundError(f"The file could not be found.")
#     return new_file_name

# def extract_law_text_from_docx(bill_path):
#     output_text = ""
#     doc = Document(bill_path)

#     #update to only include docs that haven't been posted yet
#     # find a way to determine when the actual bill text starts
#     # do I need to validate that it's a docx file


#     for para in doc.paragraphs:
#         for run in para.runs: #not sure what runs are, but these for loops seem to look through on a character by character basis (testing by strikethroughing a single character and this picks it up as an individual run)
#             if not run.font.strike: #only extract text that isn't strikethrough 
#                 output_text += run.text
#         output_text += ' ' #resolves spacing issues
#     return output_text


# def extract_and_upload_senate_bill_metadata(supa_con):
#     sen_rss = feedparser.parse(senate_rss_feed)
#     for bill in sen_rss.entries:
#         if bill is None: continue

#         bill_no = get_bill_no_from_RSS_title(bill.title, "senate")
#         printer_no = get_bill_printer_no_from_RSS_title(bill.title)
        
#         bill_path = dowload_bill_doc_file(bill["link"])
#         bill_docx_path = convert_doc_to_docx(bill_path)
#         bill_text = extract_law_text_from_docx(bill_docx_path)
#         os.remove(bill_path)
#         os.remove(bill_docx_path)

#         if has_existing_supabase_records(supa_con, bill_no, printer_no, "senate"): continue
#         supa_con.table('Revisions').insert(
#             {
#                 "bill_id": bill_no,
#                 "printer_no": printer_no, 
#                 "full_text_link": bill["link"], 
#                 "publication_date": bill["published"], 
#                 "legislative_body": "senate",
#                 "full_text": bill_text
#                 # "active_summary_id": metadata["active_summary_id"], #leaving out foreign keys for now
#             }).execute()
#     return

# def extract_and_upload_house_bill_metadata(supa_con):
#     house_rss = feedparser.parse(house_rss_feed)
#     for bill in house_rss.entries:
#         if bill is None: continue

#         bill_no = get_bill_no_from_RSS_title(bill.title, "house")
#         printer_no = get_bill_printer_no_from_RSS_title(bill.title)

#         if has_existing_supabase_records(supa_con, bill_no, printer_no, "house"): continue
#         supa_con.table('Revisions').insert(
#             {
#                 "bill_id": bill_no,
#                 "printer_no": printer_no, 
#                 "full_text_link": bill["link"], 
#                 "publication_date": bill["published"], 
#                 "legislative_body": "house"
#                 # "active_summary_id": metadata["active_summary_id"],  #leaving out foreign keys for now
#             }).execute()
#     return


# if __name__ == "__main__":
#     # print(sb_api_key)
#     supabase_connection: Client = create_client(sb_api_url, sb_api_key)
#     extract_and_upload_senate_bill_metadata(supabase_connection)
#     #extract_and_upload_house_bill_metadata(supabase_connection)

#     # tst_doc_convert()







# """
# looked into temorarily storing in vm, then manipulating files within an actions runner
# you can save to the home directory as shown here: https://medium.com/@fonseka.live/sharing-data-in-github-actions-a9841a9a6f42
# how this is actually implemented will dramatically impact how my extract law text function works
# """

# # def has_existing_bill_text_record():
# #     return 

# # # def upload_law_text_to_supabase(supa_con, bill_no, printer_no, leg_body):  
# #     # return

# # def process_docx_files(): #function to handle the scraping and uploading of all docx files
# #     # get all bills from revsions withe empty full_text fields
# #     # for each bill, post
# #     return



# # def tst_doc_convert():
# #     sample_link = "https://www.legis.state.pa.us//CFDOCS/Legis/PN/Public/btCheck.cfm?txtType=DOC&sessYr=2023&sessInd=0&billBody=H&billTyp=B&billNbr=0106&pn=1743"
# #     #download doc to runner
# #     response = requests.get(sample_link, stream=True)
# #     with open("bill.doc", "wb") as f:
# #         f.write(response.content)
    
# #     #

# #     try:
# #         subprocess.call(['libreoffice', '--headless', '--convert-to', 'docx', "bill.doc"])
# #     except FileNotFoundError:
# #         raise FileNotFoundError(f"The file could not be found.")
    
    
# #     tmp = extract_law_text("bill.docx")
# #     if os.path.isfile('bill.docx'):
# #         raise FileNotFoundError(tmp)

# #     #this demo works, now its time to create the official process

# #     return