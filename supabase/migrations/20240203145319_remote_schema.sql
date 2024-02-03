create or replace view "public"."revisions_feed_view" as  SELECT r.revision_guid,
    r.full_text_link,
    s.summary_text
   FROM ("Revisions" r
     LEFT JOIN "Summaries" s ON ((s.revision_internal_id = r.revision_internal_id)));



