from abc import ABC, abstractmethod

from law_reader import BillIdentifier


class DBInterface(ABC):
    """
    Interface for database classes.
    This is created to ensure that all database classes have the same methods, and to enhance unit testing.
    As well as to guide the implementation or replacement of the database classes.
    This class is meant to be inherited by other classes.
    All methods in this class are meant to be overridden.
    """

    def __init__(self):
        pass

    # region Basic database operations

    #endregion

    def select(self, table, columns: list[str], where_conditions: dict = None) -> list[dict[str, any]]:
        """
        Selects rows from the given table and returns them
        :param table: The name of the table to select from
        :param columns: A list of column names to select
        :param where_conditions: A dictionary defining the WHERE conditions (column: value)
        :return: The selected rows, as a list of dictionaries (column: value)
        """
        pass

    @abstractmethod
    def insert(self, table, row_column_dict: dict):
        """
        Inserts a row into the given table
        :param table: The name of the table to insert into
        :param row_column_dict: A dictionary containing the column names and values
        :return: The id of the inserted row, or None if the insert failed
        """
        pass

    #region Intermediate Database Operations

    def row_exists(self, table: str, where_conditions: dict) -> bool:
        """
        Checks if a row exists in the given table
        :param table: The name of the table to check
        :param where_conditions: A dictionary defining the WHERE conditions (column: value)
        :return: True if a row exists, False if not
        """
        pass

    #endregion

    @abstractmethod
    def get_bill_internal_id(self, bill_identifier: BillIdentifier) -> str:
        """
        Gets the bill_internal_id of a bill from the Supabase table "Bills" using the bill's legislative_id.
        :param bill_identifier: The BillIdentifier object for the bill
        :return: The bill_internal_id of the bill
        """
        pass



    @abstractmethod
    def create_and_attempt_to_insert_revision(self, revision_rss_feed_entry, bill_identifier: BillIdentifier) -> bool:
        """
        Creates a new bill revision record in the database if it does not already exist.
        :param revision_rss_feed_entry: The RSS feed entry for the bill revision
        :param bill_identifier: The BillIdentifier object for the bill
        :return: True if a new record was inserted, False if not
        """
        pass

    @abstractmethod
    def create_and_attempt_to_insert_bill(self, bill_identifier: BillIdentifier) -> bool:
        """
        Creates a new bill record in the database if it does not already exist.
        :param bill_identifier: The BillIdentifier object for the bill
        :return: True if a new record was inserted, False if not
        """
        pass

    @abstractmethod
    def download_bill_text(self, revision_guid: str) -> str:
        """
        Downloads the full text of a bill from the database
        :param revision_guid: the unique id of the bill
        :return: the full text of the bill
        """
        pass

    def upload_summary(self, revision_guid: str, summary_text: str):
        """
        Uploads a summary to the database, linking it to the appropriate entry in the "Revisions" table
        :param revision_guid: the unique id of the bill
        :param summary_text: the text of the summary
        """
        pass

    def get_revisions_without_summaries(self) -> list[str]:
        """
        Gets the unique ids of all bills without summaries
        :return: a list of unique ids of bills without summaries
        """
        pass
