import psycopg2

from law_reader import DBInterface, BillIdentifier, InvalidRTUniqueIDException
from law_reader.common.RevisionSummaryInfo import RevisionSummaryInfo


class PostgresDBInterface(DBInterface):
    """
    Interface for Postgres database classes.
    Utilizes psycopg2 library.
    """

    def __init__(self, db_password, db_host):
        super().__init__()
        self.connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=db_password,
            host=db_host,
            port="54322"
        )
        self.cursor = self.connection.cursor()

    def get_tables(self):
        self.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        return self.fetchall()

    def insert(self, table, row_column_dict: dict, return_column: str = ""):
        """
        Inserts a row into the given table
        :param table: The name of the table to insert into
        :param row_column_dict: A dictionary containing the column names and values
        :return: The id of the inserted row, or None if the insert failed
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
        self.execute("SELECT full_text FROM \"Revision_Text\" WHERE revision_guid = %s", (revision_guid,))
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
        # Insert summary into Summaries table and retrieve the summary_id of the new entry
        summary_insert_dict = {
            "summary_text": summary_text,
            "revision_guid": revision_guid
        }
        summary_id = self.insert("Summaries", summary_insert_dict, "id")
        active_summary_dict = {
            "revision_guid": revision_guid,
            "summaries_id": summary_id
        }
        # Insert summary into Active_Summaries table
        self.insert("Active_Summaries", active_summary_dict)
        return summary_id

    def get_revisions_without_summaries(self) -> list[str]:
        """
        Gets the unique ids of all bills without summaries
        :return: A list of RevisionSummaryInfo objects for the bills without summaries
        """
        self.execute("SELECT r.revision_guid FROM \"Revisions\" r "
                     "LEFT JOIN \"Active_Summaries\" a ON r.revision_guid = a.revision_guid "
                     "WHERE a.revision_guid IS NULL")
        result = self.fetchall()
        return [revision_guid for revision_guid in result]

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
