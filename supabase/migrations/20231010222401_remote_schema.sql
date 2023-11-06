alter table "public"."Revisions" drop constraint "Revisions_bill_internal_id_fkey";

alter table "public"."Revisions" alter column "bill_internal_id" set data type bigint using "bill_internal_id"::bigint;

alter table "public"."Revisions" add constraint "Revisions_bill_internal_id_fkey" FOREIGN KEY (bill_internal_id) REFERENCES "Bills"(bill_internal_id) not valid;

alter table "public"."Revisions" validate constraint "Revisions_bill_internal_id_fkey";


