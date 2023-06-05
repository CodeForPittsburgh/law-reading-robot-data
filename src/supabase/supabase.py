from supabase import create_client
import json
API_URL = 'https://kgyhcqcbqajaqyvhkdiz.supabase.co'
API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtneWhjcWNicWFqYXF5dmhrZGl6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODQ3OTk2NTksImV4cCI6MjAwMDM3NTY1OX0.ydUFo2-632RPVAgyeVYFjVmaWPNO5lYQ9NCvhK5-uy0'
supabase = create_client(API_URL, API_KEY)
supabase

data = {
    'external_id': 1,
    'title': 'Hello',
    'description': 22,
    'status': 'pending',
    'primary_sponsor_id': 1,
    'active_revision_id': 1,
    'session': 1,
    'co_sponsor_ids': json.dumps([1, 2, 3]),
    'revision_id': json.dumps([1, 2, 3]),
    'tag_ids': json.dumps([1, 2, 3]),
}
supabase.table('Bill').insert(data).execute() # inserting one record

supabase.table('Bill').select('*').execute().data # fetching documents