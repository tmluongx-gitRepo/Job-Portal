"""
Supabase client configuration and initialization.
"""
from supabase import create_client, Client
from app.config import settings


def get_supabase_client() -> Client:
    """
    Create and return Supabase client instance.
    
    Uses anon key for authentication operations.
    
    Returns:
        Client: Configured Supabase client
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise ValueError(
            "Supabase configuration missing. Please set SUPABASE_URL and "
            "SUPABASE_ANON_KEY in your environment variables."
        )
    
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )


# Global Supabase client instance
try:
    supabase: Client = get_supabase_client()
except ValueError as e:
    print(f"⚠️  Supabase client not initialized: {e}")
    supabase = None

