from fastapi import APIRouter, HTTPException,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from supabase import Client
from utils import get_supabase_client


router = APIRouter(prefix="/vendor", tags=["Vendor"])

security = HTTPBearer()

@router.get("/list")
async def list_vendors(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """List all vendors."""
    try:
        token = credentials.credentials
        client: Client = get_supabase_client(token)
        data = client.from_("vendors").select("*").execute()
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
# Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6ImdzYkYydlJ4NDhOS0pXa3ciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2p2d2lncmtob3FyaWNoZmR0Y2ZoLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyMzFmZGJiZC02OTNjLTRlMTktOTliYi1lZGZjYjQyMTNkZmQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU5MDMyNDY1LCJpYXQiOjE3NTg5NDYwNjUsImVtYWlsIjoic2h5YW1nYW5lc2hyYXZpY2hhbmRyYW40QGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnsiZW1haWwiOiJzaHlhbWdhbmVzaHJhdmljaGFuZHJhbjRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6InNoeWFtIGdhbmVzaCIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicm9sZSI6InZlbmRvciIsInNob3BfbmFtZSI6IkdhbmVzaCBHcm9jZXJ5IFNob3AiLCJzaG9wX3R5cGVzIjpbIkdyb2NlcnkiLCJTcHJvdHMiXSwic3ViIjoiMjMxZmRiYmQtNjkzYy00ZTE5LTk5YmItZWRmY2I0MjEzZGZkIn0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoicGFzc3dvcmQiLCJ0aW1lc3RhbXAiOjE3NTg5NDYwNjV9XSwic2Vzc2lvbl9pZCI6ImQyMWNmYjgwLWY5M2YtNDk0Ny04OWQyLWNmMzc1YjQ1NmY2YyIsImlzX2Fub255bW91cyI6ZmFsc2V9.0zPyqxLVyVBYME7cLEKCPiluhSbKu0V1cRBmuM8DgZw
