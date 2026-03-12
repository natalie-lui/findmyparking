import os
from supabase import create_client, Client
from dotenv import load_dotenv


load_dotenv()

url: str = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key: str = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Warning: Supabase credentials not found in environment variables.")

def get_supabase_client() -> Client:
    return create_client(url, key)
