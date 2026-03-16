import hashlib
from utils.supabase_client import get_supabase_client

supabase = get_supabase_client()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def sign_up(username, password):
    # Check if username already exists
    existing = supabase.table("users").select("id").eq("email", username).execute()
    if existing.data:
        return {"success": False, "error": "Username already taken"}

    response = supabase.table("users").insert({
        "email": username,
        "password": hash_password(password)
    }).execute()

    if response.data:
        return {"success": True, "user": response.data[0]}
    return {"success": False, "error": "Sign up failed"}

def sign_in(username, password):
    response = supabase.table("users").select("*").eq("email", username).execute()
    if not response.data:
        return {"success": False, "error": "Username not found"}

    user = response.data[0]
    if user["password"] != hash_password(password):
        return {"success": False, "error": "Incorrect password"}

    return {"success": True, "user": user}