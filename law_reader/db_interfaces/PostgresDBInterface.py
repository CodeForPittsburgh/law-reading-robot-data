import psycopg2

from law_reader import DBInterface, BillIdentifier, InvalidRTUniqueIDException, Revision


class PostgresDBInterface(DBInterface):
    """
    Interface for Postgres database classes.
    Utilizes psycopg2 library.
    """

    def __init__(self, db_password, db_host, port):
        super().__init__()
        self.connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=db_password,
            host=db_host,
            port=port
        )
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

    def download_bill_text(self, revision_guid: str) -> str:
        """
        Downloads the full text of a bill from the database, using the rt_unique_id
        Raises an InvalidRTUniqueIDException if the bill cannot be found
         or if multiple bills are found with the given rt_unique_id
        :param rt_unique_id: the unique id of the bill in the Revision_Text table
        :return: the full text of the bill
        """
        sql_script = (f"SELECT rt.full_text "
                      f"FROM \"Revision_Text\" rt, \"Revisions\" r "
                      f" WHERE r.revision_guid = '{revision_guid}'"
                      f" AND r.rt_unique_id = rt.rt_unique_id")
        self.execute(sql_script)
        result = self.fetchall()
        if result is None:
            raise InvalidRTUniqueIDException(f"Could not find bill with revision_guid {revision_guid}")
        elif len(result) > 1:
            raise InvalidRTUniqueIDException(f"Found multiple bills with revision_guid {revision_guid}")
        text = result[0][0]
        if text is None or text == "":
            raise InvalidRTUniqueIDException(f"Bill with revision_guid {revision_guid} has no text")
        return text

    def upload_summary(self, revision_guid: str, summary_text: str):
        """
        Uploads a summary to the database, linking it to the appropriate entry in the "Revisions" table
        :param revision_guid: a RevisionSummaryInfo object containing information about the revision
        :param summary_text: the text of the summary
        :return: The id of the inserted row, or None if the insert failed
        """
        # Insert summary
        return self.insert_and_link(
            row_to_insert={"summary_text": summary_text},
            table_to_insert_into="Summaries",
            column_to_return="summary_id",
            linking_table="Revisions",
            linking_column_to_update="active_summary_id",
            linking_where={"revision_guid": revision_guid}
        )

    def get_revisions_without_summaries(self) -> list[str]:
        """
        Gets the unique ids of all bills without summaries
        :return: A list of RevisionSummaryInfo objects for the bills without summaries
        """
        self.execute("SELECT r.revision_guid FROM \"Revisions\" r "
                     "WHERE r.active_summary_id IS NULL")
        result = self.fetchall()
        return [revision_guid for revision_guid in result]

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

