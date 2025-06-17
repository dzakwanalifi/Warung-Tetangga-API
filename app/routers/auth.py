# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ..core.database import get_db
from ..core.supabase_client import supabase
from ..models.profile import Profile

router = APIRouter()

# --- Pydantic Schemas untuk Request Body ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Endpoints ---

@router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Mendaftarkan user baru via Supabase dan membuat profil lokal.
    """
    try:
        # 1. Daftarkan user ke Supabase Auth
        res = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })

        # Periksa apakah user berhasil dibuat di Supabase
        if res.user is None or res.user.id is None:
            raise HTTPException(status_code=400, detail="Could not create user in Supabase")

        # 2. Buat profil di tabel 'profiles' kita
        new_profile = Profile(
            id=res.user.id,
            full_name=user_data.full_name
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        return {"message": "Registration successful, please check your email to confirm.", "session": res.session}

    except Exception as e:
        # Tangani error jika user sudah ada atau error lainnya dari Supabase
        if "already registered" in str(e):
            raise HTTPException(status_code=400, detail="User with this email already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(user_data: UserLogin):
    """
    Login user menggunakan Supabase Auth.
    """
    try:
        res = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        return res
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid login credentials: {e}") 