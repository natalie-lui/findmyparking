from utils.supabase_client import get_supabase_client

supabase = get_supabase_client()

def log_parking(user_id, spot):
    supabase.table("parking_history").insert({
        "user_id": user_id,
        "spot_name": spot["name"],
        "spot_lat": spot["lat"],
        "spot_lon": spot["lon"],
        "cost_per_hour": spot["cost_per_hour"],
        "walk_time_minutes": spot["walk_time_minutes"],
    }).execute()
    
def get_user_history(user_id):
    response = supabase.table("parking_history") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("parked_at", desc=True) \
        .execute()
    return response.data or []