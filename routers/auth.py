from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from config import settings
from typing import Literal, Optional

# Initialize Supabase client
url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/auth", tags=["Auth"])
class UserCredentials(BaseModel):
    email: str
    password: str
    full_name: str
    role: Literal["customer", "vendor"] = "customer"
    shop_name: Optional[str] = None
    shop_types: Optional[list[str]] = None

@router.post("/signup")
async def signup(credentials: UserCredentials):
    """Create a new user."""
    try:
        user = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password,
            "options":{
                "data": {
                    "full_name": credentials.full_name,
                    "role": credentials.role,
                    "shop_name": credentials.shop_name,
                    "shop_types": credentials.shop_types,
                }
            }
        })
        return {"message": "User created successfully", "user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin")
async def signin(credentials: UserCredentials):
    """Sign in an existing user."""
    try:
        user = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })
        return {"message": "User signed in successfully", "user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
