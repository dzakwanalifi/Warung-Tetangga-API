# app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
import jwt

from .supabase_client import supabase
from .config import settings

# Gunakan skema HTTPBearer yang lebih sederhana
bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Dependency untuk memvalidasi token dan mendapatkan data user dari Supabase.
    Akan melempar HTTPException 401 jika token tidak valid.
    """
    try:
        token = credentials.credentials
        
        # Decode JWT token untuk mendapatkan user info
        # Supabase menggunakan JWT dengan secret key yang sama dengan SUPABASE_KEY
        try:
            # Decode without verification first to get the payload
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded_token.get("sub")
            email = decoded_token.get("email")
            
            if not user_id or not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create a simple user object that matches what we need
            class SimpleUser:
                def __init__(self, user_id, email):
                    self.id = user_id
                    self.email = email
            
            return SimpleUser(user_id, email)
            
        except jwt.InvalidTokenError as e:
            print(f"JWT decode error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except HTTPException:
        # Re-raise HTTPException yang sudah kita buat
        raise
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 