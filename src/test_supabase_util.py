from unittest import TestCase
from supabase_util import get_client

class Test(TestCase):

    # Setup
    def setUp(self):
        self.client = get_client()

    def test_get_client(self):
        print(
            self.client
        )

    def test_select(self):
        print(self.client.table('Bills').select("*").execute())

    def test_insert(self):
        # TODO: Test insert
        pass

    def test_update(self):
        # TODO: Test update
        pass

