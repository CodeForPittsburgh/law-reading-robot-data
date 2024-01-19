drop policy "Enable insert for authenticated users only" on "public"."Policy_Test";

drop policy "Enable read access for all users" on "public"."bill_revisions";

drop policy "Enable read access for all users" on "public"."bill_sponsors";

drop policy "Enable read access for all users" on "public"."bill_tags";

drop policy "Enable read access for all users" on "public"."revisions";

drop policy "Enable read access for all users" on "public"."sponsor_table";

drop policy "Enable read access for all users" on "public"."tags";

revoke delete on table "public"."Policy_Test" from "anon";

revoke insert on table "public"."Policy_Test" from "anon";

revoke references on table "public"."Policy_Test" from "anon";

revoke select on table "public"."Policy_Test" from "anon";

revoke trigger on table "public"."Policy_Test" from "anon";

revoke truncate on table "public"."Policy_Test" from "anon";

revoke update on table "public"."Policy_Test" from "anon";

revoke delete on table "public"."Policy_Test" from "authenticated";

revoke insert on table "public"."Policy_Test" from "authenticated";

revoke references on table "public"."Policy_Test" from "authenticated";

revoke select on table "public"."Policy_Test" from "authenticated";

revoke trigger on table "public"."Policy_Test" from "authenticated";

revoke truncate on table "public"."Policy_Test" from "authenticated";

revoke update on table "public"."Policy_Test" from "authenticated";

revoke delete on table "public"."Policy_Test" from "service_role";

revoke insert on table "public"."Policy_Test" from "service_role";

revoke references on table "public"."Policy_Test" from "service_role";

revoke select on table "public"."Policy_Test" from "service_role";

revoke trigger on table "public"."Policy_Test" from "service_role";

revoke truncate on table "public"."Policy_Test" from "service_role";

revoke update on table "public"."Policy_Test" from "service_role";

revoke delete on table "public"."bill_revisions" from "anon";

revoke insert on table "public"."bill_revisions" from "anon";

revoke references on table "public"."bill_revisions" from "anon";

revoke select on table "public"."bill_revisions" from "anon";

revoke trigger on table "public"."bill_revisions" from "anon";

revoke truncate on table "public"."bill_revisions" from "anon";

revoke update on table "public"."bill_revisions" from "anon";

revoke delete on table "public"."bill_revisions" from "authenticated";

revoke insert on table "public"."bill_revisions" from "authenticated";

revoke references on table "public"."bill_revisions" from "authenticated";

revoke select on table "public"."bill_revisions" from "authenticated";

revoke trigger on table "public"."bill_revisions" from "authenticated";

revoke truncate on table "public"."bill_revisions" from "authenticated";

revoke update on table "public"."bill_revisions" from "authenticated";

revoke delete on table "public"."bill_revisions" from "service_role";

revoke insert on table "public"."bill_revisions" from "service_role";

revoke references on table "public"."bill_revisions" from "service_role";

revoke select on table "public"."bill_revisions" from "service_role";

revoke trigger on table "public"."bill_revisions" from "service_role";

revoke truncate on table "public"."bill_revisions" from "service_role";

revoke update on table "public"."bill_revisions" from "service_role";

revoke delete on table "public"."bill_sponsors" from "anon";

revoke insert on table "public"."bill_sponsors" from "anon";

revoke references on table "public"."bill_sponsors" from "anon";

revoke select on table "public"."bill_sponsors" from "anon";

revoke trigger on table "public"."bill_sponsors" from "anon";

revoke truncate on table "public"."bill_sponsors" from "anon";

revoke update on table "public"."bill_sponsors" from "anon";

revoke delete on table "public"."bill_sponsors" from "authenticated";

revoke insert on table "public"."bill_sponsors" from "authenticated";

revoke references on table "public"."bill_sponsors" from "authenticated";

revoke select on table "public"."bill_sponsors" from "authenticated";

revoke trigger on table "public"."bill_sponsors" from "authenticated";

revoke truncate on table "public"."bill_sponsors" from "authenticated";

revoke update on table "public"."bill_sponsors" from "authenticated";

revoke delete on table "public"."bill_sponsors" from "service_role";

revoke insert on table "public"."bill_sponsors" from "service_role";

revoke references on table "public"."bill_sponsors" from "service_role";

revoke select on table "public"."bill_sponsors" from "service_role";

revoke trigger on table "public"."bill_sponsors" from "service_role";

revoke truncate on table "public"."bill_sponsors" from "service_role";

revoke update on table "public"."bill_sponsors" from "service_role";

revoke delete on table "public"."bill_tags" from "anon";

revoke insert on table "public"."bill_tags" from "anon";

revoke references on table "public"."bill_tags" from "anon";

revoke select on table "public"."bill_tags" from "anon";

revoke trigger on table "public"."bill_tags" from "anon";

revoke truncate on table "public"."bill_tags" from "anon";

revoke update on table "public"."bill_tags" from "anon";

revoke delete on table "public"."bill_tags" from "authenticated";

revoke insert on table "public"."bill_tags" from "authenticated";

revoke references on table "public"."bill_tags" from "authenticated";

revoke select on table "public"."bill_tags" from "authenticated";

revoke trigger on table "public"."bill_tags" from "authenticated";

revoke truncate on table "public"."bill_tags" from "authenticated";

revoke update on table "public"."bill_tags" from "authenticated";

revoke delete on table "public"."bill_tags" from "service_role";

revoke insert on table "public"."bill_tags" from "service_role";

revoke references on table "public"."bill_tags" from "service_role";

revoke select on table "public"."bill_tags" from "service_role";

revoke trigger on table "public"."bill_tags" from "service_role";

revoke truncate on table "public"."bill_tags" from "service_role";

revoke update on table "public"."bill_tags" from "service_role";

revoke delete on table "public"."revisions" from "anon";

revoke insert on table "public"."revisions" from "anon";

revoke references on table "public"."revisions" from "anon";

revoke select on table "public"."revisions" from "anon";

revoke trigger on table "public"."revisions" from "anon";

revoke truncate on table "public"."revisions" from "anon";

revoke update on table "public"."revisions" from "anon";

revoke delete on table "public"."revisions" from "authenticated";

revoke insert on table "public"."revisions" from "authenticated";

revoke references on table "public"."revisions" from "authenticated";

revoke select on table "public"."revisions" from "authenticated";

revoke trigger on table "public"."revisions" from "authenticated";

revoke truncate on table "public"."revisions" from "authenticated";

revoke update on table "public"."revisions" from "authenticated";

revoke delete on table "public"."revisions" from "service_role";

revoke insert on table "public"."revisions" from "service_role";

revoke references on table "public"."revisions" from "service_role";

revoke select on table "public"."revisions" from "service_role";

revoke trigger on table "public"."revisions" from "service_role";

revoke truncate on table "public"."revisions" from "service_role";

revoke update on table "public"."revisions" from "service_role";

revoke delete on table "public"."sponsor_table" from "anon";

revoke insert on table "public"."sponsor_table" from "anon";

revoke references on table "public"."sponsor_table" from "anon";

revoke select on table "public"."sponsor_table" from "anon";

revoke trigger on table "public"."sponsor_table" from "anon";

revoke truncate on table "public"."sponsor_table" from "anon";

revoke update on table "public"."sponsor_table" from "anon";

revoke delete on table "public"."sponsor_table" from "authenticated";

revoke insert on table "public"."sponsor_table" from "authenticated";

revoke references on table "public"."sponsor_table" from "authenticated";

revoke select on table "public"."sponsor_table" from "authenticated";

revoke trigger on table "public"."sponsor_table" from "authenticated";

revoke truncate on table "public"."sponsor_table" from "authenticated";

revoke update on table "public"."sponsor_table" from "authenticated";

revoke delete on table "public"."sponsor_table" from "service_role";

revoke insert on table "public"."sponsor_table" from "service_role";

revoke references on table "public"."sponsor_table" from "service_role";

revoke select on table "public"."sponsor_table" from "service_role";

revoke trigger on table "public"."sponsor_table" from "service_role";

revoke truncate on table "public"."sponsor_table" from "service_role";

revoke update on table "public"."sponsor_table" from "service_role";

revoke delete on table "public"."tags" from "anon";

revoke insert on table "public"."tags" from "anon";

revoke references on table "public"."tags" from "anon";

revoke select on table "public"."tags" from "anon";

revoke trigger on table "public"."tags" from "anon";

revoke truncate on table "public"."tags" from "anon";

revoke update on table "public"."tags" from "anon";

revoke delete on table "public"."tags" from "authenticated";

revoke insert on table "public"."tags" from "authenticated";

revoke references on table "public"."tags" from "authenticated";

revoke select on table "public"."tags" from "authenticated";

revoke trigger on table "public"."tags" from "authenticated";

revoke truncate on table "public"."tags" from "authenticated";

revoke update on table "public"."tags" from "authenticated";

revoke delete on table "public"."tags" from "service_role";

revoke insert on table "public"."tags" from "service_role";

revoke references on table "public"."tags" from "service_role";

revoke select on table "public"."tags" from "service_role";

revoke trigger on table "public"."tags" from "service_role";

revoke truncate on table "public"."tags" from "service_role";

revoke update on table "public"."tags" from "service_role";

revoke delete on table "public"."test" from "anon";

revoke insert on table "public"."test" from "anon";

revoke references on table "public"."test" from "anon";

revoke select on table "public"."test" from "anon";

revoke trigger on table "public"."test" from "anon";

revoke truncate on table "public"."test" from "anon";

revoke update on table "public"."test" from "anon";

revoke delete on table "public"."test" from "authenticated";

revoke insert on table "public"."test" from "authenticated";

revoke references on table "public"."test" from "authenticated";

revoke select on table "public"."test" from "authenticated";

revoke trigger on table "public"."test" from "authenticated";

revoke truncate on table "public"."test" from "authenticated";

revoke update on table "public"."test" from "authenticated";

revoke delete on table "public"."test" from "service_role";

revoke insert on table "public"."test" from "service_role";

revoke references on table "public"."test" from "service_role";

revoke select on table "public"."test" from "service_role";

revoke trigger on table "public"."test" from "service_role";

revoke truncate on table "public"."test" from "service_role";

revoke update on table "public"."test" from "service_role";

alter table "public"."bill_revisions" drop constraint "bill_revisions_bill_internal_id_fkey";

alter table "public"."bill_revisions" drop constraint "bill_revisions_revision_id_fkey";

alter table "public"."bill_sponsors" drop constraint "bill_sponsors_bill_id_fkey";

alter table "public"."bill_sponsors" drop constraint "bill_sponsors_sponsor_id_fkey";

alter table "public"."bill_tags" drop constraint "bill_tags_bill_internal_id_fkey";

alter table "public"."bill_tags" drop constraint "bill_tags_tag_id_fkey";

alter table "public"."sponsor_table" drop constraint "sponsor_table_party_check";

alter table "public"."Policy_Test" drop constraint "Policy_Test_pkey";

alter table "public"."bill_revisions" drop constraint "bill_revisions_pkey";

alter table "public"."bill_sponsors" drop constraint "bill_sponsors_pkey";

alter table "public"."bill_tags" drop constraint "bill_tags_pkey";

alter table "public"."revisions" drop constraint "revisions_pkey";

alter table "public"."sponsor_table" drop constraint "sponsor_table_pkey";

alter table "public"."tags" drop constraint "tags_pkey";

alter table "public"."test" drop constraint "test_pkey";

drop index if exists "public"."Policy_Test_pkey";

drop index if exists "public"."bill_revisions_pkey";

drop index if exists "public"."bill_sponsors_pkey";

drop index if exists "public"."bill_tags_pkey";

drop index if exists "public"."revisions_pkey";

drop index if exists "public"."sponsor_table_pkey";

drop index if exists "public"."tags_pkey";

drop index if exists "public"."test_pkey";

drop table "public"."Policy_Test";

drop table "public"."bill_revisions";

drop table "public"."bill_sponsors";

drop table "public"."bill_tags";

drop table "public"."revisions";

drop table "public"."sponsor_table";

drop table "public"."tags";

drop table "public"."test";

alter table "public"."Revisions" drop column "bill_id";

drop sequence if exists "public"."revisions_internal_id_seq";

drop sequence if exists "public"."sponsor_table_internal_id_seq";

drop sequence if exists "public"."tags_internal_id_seq";


