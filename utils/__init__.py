from fastapi.security import HTTPBearer
from supabase import create_client
from config import settings


url: str = settings.SUPABASE_URL
supabase_key: str = settings.SUPABASE_KEY


security = HTTPBearer()

def get_supabase_client(auth_token: str):
    token = auth_token.split(" ")[1] 
    # Create a client with the user's token -> respects RLS
    client = create_client(url, supabase_key)
    client.postgrest.auth(token)
    return client
    