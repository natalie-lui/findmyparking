from utils.supabase_client import get_supabase_client

supabase = get_supabase_client()

def sign_up(email, password):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "email_redirect_to": None  # no confirmation email
            }
        })
        # If email confirmation is off, user is returned immediately
        if res.user:
            return {"success": True, "user": res.user}
        else:
            return {"success": False, "error": "Sign up failed. Try a different email."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def sign_in(email, password):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if res.user:
            return {"success": True, "user": res.user}
        else:
            return {"success": False, "error": "Invalid email or password."}
    except Exception as e:
        return {"success": False, "error": str(e)}