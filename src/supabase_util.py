import supabase
import os

def get_client():
    """
    Get LawReadingRobotData Supabase client.
    Accessing requires "SUPABASE_API_KEY" environment variable to be set.
    :return:
    """
    return supabase.create_client(
        supabase_url="https://vsumrxhpkzegrktbtcui.supabase.co",
        supabase_key=os.environ['SUPABASE_API_KEY']
    )