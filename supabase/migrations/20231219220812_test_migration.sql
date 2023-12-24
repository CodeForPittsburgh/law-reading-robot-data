create table public.test(
    id integer primary key generated always as identity,
    name text
);