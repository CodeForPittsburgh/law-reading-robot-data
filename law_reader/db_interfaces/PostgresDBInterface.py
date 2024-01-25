import os

import psycopg2
from dotenv import load_dotenv

from law_reader.common.RevisionSummaryInfo import RevisionSummaryInfo
from law_reader import BillIdentifier, Revision
from law_reader.db_interfaces import DBInterface
from law_reader.summarizer.InvalidRTUniqueIDException import InvalidRTUniqueIDException


class PostgresDBInterface(DBInterface):
    """
    Interface for Postgres database classes.
    Utilizes psycopg2 library.
    """

    def __init__(self):
        super().__init__()
        load_dotenv()  # Load environment variables from .env file

        try:
            # Attempt to establish a connection
            self.connection = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password=os.environ["SUPABASE_DB_PASSWORD"],
                host=os.environ["SUPABASE_DB_HOST"],
                port=os.environ["SUPABASE_DB_PORT"]
            )
        except KeyError as e:
            # Handle missing environment variables
            print(f"Environment variable not found: {e}")
        except psycopg2.OperationalError as e:
            # Handle database connection errors
            print(f"Database connection failed: {e}")
        else:
            print("Database connection established successfully.")
        self.cursor = self.connection.cursor()


    #region Basic database operations
    def get_tables(self):
        self.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        return self.fetchall()

    def select(self, table, columns: list[str], where_conditions: dict = None) -> list[dict[str, any]]:
        """
        Selects rows from the given table and returns them
        :param table: The name of the table to select from
        :param columns: A list of column names to select
        :param where_conditions: A dictionary defining the WHERE conditions (column: value)
        :return: The selected rows, as a list of dictionaries (column: value)
        """
        sql_script = f"SELECT "
        for column in columns:
            sql_script += f"{column}, "
        sql_script = sql_script[:-2] + f" FROM \"{table}\""
        if where_conditions is not None:
            sql_script += " WHERE "
            for column in where_conditions.keys():
                sql_script += f"{column} = %s AND "
            sql_script = sql_script[:-5]
            self.execute(sql_script, list(where_conditions.values()))
        else:
            self.execute(sql_script)
        result = self.fetchall()
        # Convert to list of dictionaries
        return [dict(zip(columns, row)) for row in result]

    def insert(self, table, row_column_dict: dict, return_column: str = ""):
        """
        Inserts a row into the given table
        :param table: The name of the table to insert into
        :param row_column_dict: A dictionary containing the column names and values
        :param return_column: The column to return
        :return: The id of the return column, or None
        """
        sql_script = f"INSERT INTO \"{table}\" ("
        for column in row_column_dict.keys():
            sql_script += f"{column}, "
        sql_script = sql_script[:-2] + ") VALUES ("
        for column in row_column_dict.keys():
            sql_script += f"%({column})s, "
        sql_script = sql_script[:-2] + ")"
        if return_column != "":
            sql_script += f" RETURNING {return_column}"
        self.execute(sql_script, row_column_dict)
        if return_column != "":
            return self.fetchone()[0]

    def update(self, table, row_column_dict: dict, where_conditions: dict):
        """
        Updates a row in the given table
        :param table: The name of the table to update
        :param row_column_dict: A dictionary containing the column names and values
        :param where_conditions: A dictionary defining the WHERE conditions (column: value)
        """
        try:
            sql_script = f"UPDATE \"{table}\" SET "
            sql_script += ', '.join([f"{column} = %s" for column in row_column_dict.keys()])
            sql_script += " WHERE " + ' AND '.join([f"{column} = %s" for column in where_conditions.keys()])

            self.execute(sql_script, list(row_column_dict.values()) + list(where_conditions.values()))
        except Exception as e:
            print(f"Database error during update: {e}")
            self.rollback()
            raise

    def begin_transaction(self):
        self.execute("BEGIN")

    def close(self):
        self.cursor.close()
        self.connection.close()

    def execute(self, query, params=None):
        self.cursor.execute(query, params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    #endregion

    #region Intermediate database operations
    """
    These operations are built on top of the basic operations 
    but are not specific to any one table.
    """

    def row_exists(self, table: str, where_conditions: dict) -> bool:
        """
        Checks if a row exists in the given table
        :param table: The name of the table to check
        :param where_conditions: A dictionary defining the WHERE conditions (column: value)
        :return: True if a row exists, False if not
        """
        sql_script = f"SELECT * FROM \"{table}\" WHERE "
        sql_script += ' AND '.join([f"{column} = %s" for column in where_conditions.keys()])
        self.execute(sql_script, list(where_conditions.values()))

        result = self.fetchall()
        # If more than one row was returned, throw an error
        if len(result) > 1:
            raise Exception("More than one row was returned")
        return len(result) == 1


    def insert_and_link(
            self,
            row_to_insert: dict,
            table_to_insert_into: str,
            column_to_return: str,
            linking_table: str,
            linking_column_to_update: str,
            linking_where: dict,
    ):
        """
        Inserts a row into the given table, and links it to the given row in the linking table
        :param row_to_insert: A dictionary containing the column names and values
        :param table_to_insert_into: The name of the table to insert into
        :param column_to_return: The column to return
        :param linking_table: The name of the linking table
        :param linking_column_to_update: The column in the linking table updated with the id of the inserted row
        :param linking_where: A dictionary defining the WHERE conditions (column: value)
        :return: The id of the inserted row, or None if the insert failed
        """
        try:
            self.begin_transaction()

            # Insert row and get ID
            row_id = self.insert(
                table_to_insert_into, row_to_insert, column_to_return)
            if not row_id:
                raise ValueError("Failed to insert row")

            # Update corresponding row in linking table
            self.update(
                table=linking_table,
                row_column_dict={linking_column_to_update: row_id},
                where_conditions=linking_where
            )

            # Commit transaction
            self.commit()
            return row_id
        except Exception as e:
            print(f"Error in insert_and_link: {e}")
            self.rollback()
            raise



    #endregion


    #region Specialized operations
    """
    These operations are specialized and are specific to 
    a particular table or set of tables.
    """
    def get_bill_internal_id(self, bill_identifier: BillIdentifier) -> str:
        pass

    def create_and_attempt_to_insert_revision(self, revision_rss_feed_entry, bill_identifier: BillIdentifier) -> bool:
        pass

    def create_and_attempt_to_insert_bill(self, bill_identifier: BillIdentifier) -> bool:
        pass

    def download_bill_text(self, rt_unique_id: str) -> str:
        """
        Downloads the full text of a bill from the database, using the rt_unique_id
        Raises an InvalidRTUniqueIDException if the bill cannot be found
         or if multiple bills are found with the given rt_unique_id
        :param rt_unique_id: the unique id of the bill in the Revision_Text table
        :return: the full text of the bill
        """
        sql_script = f"SELECT full_text FROM \"Revision_Text\" WHERE rt_unique_id = '{rt_unique_id}'"
        self.execute(sql_script)
        result: list[tuple] = self.fetchall()
        if len(result) < 1:
            raise InvalidRTUniqueIDException(f"Could not find bill with rt_unique_id {rt_unique_id}")
        elif len(result) > 1:
            raise InvalidRTUniqueIDException(f"Found multiple bills with rt_unique_id {rt_unique_id}")
        text = result[0][0]
        if text is None or text == "":
            raise InvalidRTUniqueIDException(f"Bill with rt_unique_id {rt_unique_id} has no text")
        return text

    def upload_summary(self, revision_guid: str, summary_text: str):
        """
        Uploads a summary to the database, linking it to the appropriate entry in the "Revisions" table
        :param revision_guid: a RevisionSummaryInfo object containing information about the revision
        :param summary_text: the text of the summary
        :return: The id of the inserted row, or None if the insert failed
        """
        # Get revision internal id
        revision_internal_id = self.get_revision_internal_id(revision_guid)

        # Set all existing summaries for the revision to inactive
        sql_script = f"UPDATE public.\"Summaries\" "\
                        f"SET is_active_summary = false "\
                        f"WHERE revision_internal_id = {revision_internal_id}; "
        # Execute script
        self.execute(sql_script)
        # Insert the new summary
        sql_script = f"INSERT INTO public.\"Summaries\" (revision_internal_id, summary_text, is_active_summary) "\
                        f"VALUES ({revision_internal_id}, '{summary_text}', true)" \
                        f"RETURNING summary_id "
        # Execute script
        self.execute(sql_script)
        summary_id = self.fetchone()[0]

        self.commit()
        # Return id of inserted row
        return summary_id

    def get_revisions_without_summaries(self) -> list[RevisionSummaryInfo]:
        """
        Gets the unique ids of all bills without summaries
        :return: A list of RevisionSummaryInfo objects for the bills without summaries
        """
        sql_script = (f"SELECT r.revision_guid, r.rt_unique_id, r.revision_internal_id "
                      f"FROM \"Revisions\" r "
                      f"LEFT JOIN public.\"Summaries\" s "
                      f"ON r.revision_internal_id = s.revision_internal_id "
                      f"WHERE s.is_active_summary = false "
                      f"OR s.is_active_summary IS NULL")
        self.execute(sql_script)
        result = self.fetchall()
        return [RevisionSummaryInfo(revision_guid=row[0], rt_unique_id=row[1], revision_internal_id=row[2]) for row in result]

    def get_revision_internal_id(self, revision_guid: str) -> str:
        """
        Gets the revision_internal_id of a bill from the database
        :param revision_guid: the unique id of the bill
        :return: the revision_internal_id of the bill
        """
        sql_script = f"SELECT revision_internal_id FROM \"Revisions\" WHERE revision_guid = '{revision_guid}'"
        self.execute(sql_script)
        result = self.fetchall()
        if result is None:
            raise InvalidRTUniqueIDException(f"Could not find bill with revision_guid {revision_guid}")
        elif len(result) > 1:
            raise InvalidRTUniqueIDException(f"Found multiple bills with revision_guid {revision_guid}")
        return result[0][0]


    def add_revision(self, bill_identifier: BillIdentifier, revision: Revision):
        """
        Adds a revision to the database if it does not already exist.
        If the associated bill does not exist, it is added as well
        :param bill_identifier: a BillIdentifier object containing information about the bill and revision
        :param revision: a Revision object containing information about the revision
        """

        # If revision already exists, do nothing
        if self.row_exists("Revisions", {"revision_guid": bill_identifier.revision_guid}):
            return

        # Attempt to retrieve existing bill
        select_results = self.select(
            table="Bills",
            columns=["bill_internal_id"],
            where_conditions={"legislative_id": bill_identifier.bill_guid}
        )
        # If bill exists, retrieve bill_internal_id
        if len(select_results) == 1:
            bill_internal_id = select_results[0]["bill_internal_id"]
        # If more than one entry was returned, throw an error
        elif len(select_results) > 1:
            raise Exception("More than one row was returned")
        # If bill does not exist, insert it
        else:
            bill_internal_id = self.insert(
                table="Bills",
                row_column_dict={
                    "legislative_id": bill_identifier.bill_guid,
                    "bill_number": bill_identifier.bill_number,
                    "session_type": bill_identifier.session_type,
                    "chamber": bill_identifier.chamber,
                    "legislative_session": bill_identifier.legislative_session
                },
                return_column="bill_internal_id"
            )

        # Insert revision
        self.insert(
            table="Revisions",
            row_column_dict={
                "bill_internal_id": bill_internal_id,
                "printer_no": revision.printer_no,
                "full_text_link": revision.full_text_link,
                "publication_date": revision.publication_date,
                "revision_guid": revision.revision_guid,
                "description": revision.description
            }
        )



    #endregion

    #region docx_etl
    def get_revisions_without_bill_text(self) -> list[Revision]:
        """
        Gets the unique ids of all revisions without bill text
        :return: a list of Revision objects of bills without bill text, containing the revision_guid and full_text_link
        """
        # Bill texts are stored in the Revision_Text table.
        # Revisions without text will not have an entry in this table.
        # Thus, must find revisions without an entry in the Revision_Text table.
        result = self.execute("SELECT revision_guid, full_text_link "
                              "FROM \"Revisions\" "
                              "LEFT JOIN public.\"Revision_Text\" "
                              "ON \"Revisions\".rt_unique_id = \"Revision_Text\".rt_unique_id "
                              "WHERE \"Revision_Text\".rt_unique_id IS NULL;")
        result = self.fetchall()
        return [Revision(revision_guid=row[0], full_text_link=row[1]) for row in result]


    def upload_bill_text(self, full_text: str, revision_guid: str):
        """
        Uploads the law text from a .docx file to Supabase's "Revision_Text" table,
        linking it to the appropriate entry in the "Revisions" table
        :param full_text: full text of the bill revision
        :param revision_guid: guid of the bill revision
        """
        # Insert full text into Revisions_Text table, then get rt_unique_id of the new entry
        rt_unique_id = self.insert(
            table="Revision_Text",
            row_column_dict={
                "full_text": full_text
            },
            return_column="rt_unique_id"
        )
        # Update relevant entry in Revisions table (found with revision guid) with rt_unique_id of  new entry in Revision_Text table
        self.update(
            table="Revisions",
            row_column_dict={
                "rt_unique_id": rt_unique_id
            },
            where_conditions={
                "revision_guid": revision_guid
            }
        )


    #endregion

