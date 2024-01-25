alter table "public"."Revisions" drop constraint "Revisions_active_summary_id_fkey";

alter table "public"."Revisions" drop column "active_summary_id";

alter table "public"."Summaries" add column "is_active_summary" boolean not null default false;

alter table "public"."Summaries" alter column "revision_internal_id" set not null;

CREATE UNIQUE INDEX idx_unique_active_summary_per_revision ON public."Summaries" USING btree (revision_internal_id) WHERE is_active_summary;


