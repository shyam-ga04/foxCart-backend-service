from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from routers import auth,vendor
from supabase import Client
from utils import get_supabase_client
from middleware import SupabaseAuthMiddleware

app = FastAPI()

# app.add_middleware(SupabaseAuthMiddleware)

security = HTTPBearer()

@app.get("/")
def read_root(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        client: Client = get_supabase_client(token)
        data = client.from_("vendors").select("*").execute()
        return data
    except Exception as e:
        return {"error": str(e)}

app.include_router(auth.router)

app.include_router(vendor.router)