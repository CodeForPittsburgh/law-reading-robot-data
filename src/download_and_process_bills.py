

for chamber in ("House", "Senate"):
  rss_feed = get_rss_feed(chamber)
  for entry in rss_feed:
    metadata = extract_metadata(entry)
    link = extract_link(metadata)
    doc_file = download_doc_file(link)
    docx_file = convert_to_docx(doc_file)
    law_text = extract_law_text(docx_file)
    upload_to_supabase(metadata, law_text)
