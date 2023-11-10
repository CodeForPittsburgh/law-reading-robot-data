# How to use Supabase Dev Environment

For full Supabase-provided documentation, go [here](https://supabase.com/docs/guides/cli/local-development)

## Prerequisites

- [Install Docker](https://docs.docker.com/get-docker/)
- [Install Supabase Command Line Interface (CLI)](https://github.com/supabase/cli)

## Running the Dev Environment
1. Start Docker
2. After ensuring that docker is running, type `supabase start` from the command line in the root directory, which uses Docker to start supabase services (this command may take a while if it’s your first time using the CLI)
3. This will generate a series of urls and keys. For basic development roles, note the values for “API URL” and “service_role key” and record them in a .env file which you create and place in the root directory of the repository, in the following format:
```
SUPABASE_API_URL=YOUR_API_URL
SUPABASE_API_KEY=YOUR_SERVICE_ROLE_KEY
```
4. You can now access the Local Supabase Dashboard at http://localhost:54323/ (unless configured otherwise)
5. In the Supabase Dashboard, copy and paste the migration script `primary_migration.sql` into the SQL Editor at address http://localhost:54323/project/default/sql/new
6. You are now good to run scripts on the dev environment database.
7. To stop the dev environment, type `supabase stop`

## How to delete data from SQL tables in the Supabase dev environment 

This will remove all row data from all tables in the database, but will not delete the tables themselves.

```postgresql
DO
$$
DECLARE
    r RECORD;
BEGIN
    -- Disable triggers to avoid issues with foreign keys and other constraints
    EXECUTE 'SET session_replication_role = replica;';

    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE;';
    END LOOP;

    -- Enable triggers again
    EXECUTE 'SET session_replication_role = DEFAULT;';
END
$$;

```
end;

## How to delete SQL tables in the Supabase dev environment

This is a quick and dirty way to reset the database. It will delete all tables in the database, so use with caution.

```postgresql
do $$ declare
    r record;
begin
    for r in (select tablename from pg_tables where schemaname = 'public') loop
        execute 'drop table if exists ' || quote_ident(r.tablename) || ' cascade';
    end loop;
end $$;
```

## Initial Setup (Admin Only)

1. Type `supabase init` from the command line in the root directory to setup configuration for developing locally
2. If not already logged in, type `supabase login` and follow the prompts
3. Link local Supabase project to Supabase Cloud project by typing `supabase link  --project-ref vsumrxhpkzegrktbtcui`
   1. Note that is project reference ID is specific to the Supabase project. This is found in the Supabase Cloud project settings.
4. To pull most recent version of project database, type `supabase db pull` and then enter database password. This command will create a migration script in your local `supabase/migrations` directory.
