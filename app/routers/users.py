# app/routers/users.py

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models.profile import Profile
from ..schemas.profile import ProfileSchema, ProfileUpdate

# Untuk konversi Lat/Lon ke format WKT yang dipahami PostGIS
from shapely.geometry import Point
from geoalchemy2.shape import from_shape

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=ProfileSchema)
def read_users_me(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Mendapatkan profil dari pengguna yang sedang login.
    """
    # Convert current_user.id string to UUID
    current_user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    
    profile = db.query(Profile).filter(Profile.id == current_user_uuid).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/me", response_model=ProfileSchema)
def update_users_me(
    profile_update: ProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Memperbarui profil dari pengguna yang sedang login.
    Termasuk memperbarui lokasi (lat/lon).
    """
    # Convert current_user.id string to UUID
    current_user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    
    profile = db.query(Profile).filter(Profile.id == current_user_uuid).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update data dari request body
    update_data = profile_update.model_dump(exclude_unset=True)

    # Handle update lokasi secara khusus
    if 'latitude' in update_data and 'longitude' in update_data:
        lat = update_data.pop('latitude')
        lon = update_data.pop('longitude')
        # Konversi lat/lon ke format WKT (Well-Known Text) untuk PostGIS
        # SRID 4326 adalah standar untuk GPS
        profile.location = from_shape(Point(lon, lat), srid=4326)

    # Update field lainnya
    for key, value in update_data.items():
        setattr(profile, key, value)
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile 