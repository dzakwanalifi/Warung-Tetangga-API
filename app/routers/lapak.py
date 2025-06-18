from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from geoalchemy2 import WKTElement
from typing import List, Optional
from decimal import Decimal
import uuid

from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models.listing import Listing
from ..models.profile import Profile
from ..schemas.lapak import LapakCreate, LapakSchema, LapakListResponse, LapakUpdate
from ..services import azure_storage
from ..services.gemini import analyze_image_from_file, LapakAnalysisResult

router = APIRouter()

@router.post("/analyze", response_model=LapakAnalysisResult, tags=["AI"])
def analyze_image(
    image: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Menerima file gambar, menganalisisnya langsung dengan Gemini,
    dan mengembalikan saran untuk form lapak.
    """
    # Validasi file type
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Panggil fungsi service yang baru - langsung analisis tanpa upload ke Azure
        analysis_result = analyze_image_from_file(image)
        return analysis_result
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in image analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")

@router.post("", status_code=status.HTTP_201_CREATED, response_model=LapakSchema)
def create_lapak(
    # Gunakan Form untuk data dan File untuk upload
    title: str = Form(...),
    description: Optional[str] = Form(None),
    price: Decimal = Form(...),
    unit: str = Form(...),
    stock_quantity: int = Form(...),
    images: List[UploadFile] = File(...),  # Terima file gambar
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Membuat postingan "Lapak Warga" baru dengan upload gambar.
    Pengguna harus sudah login dan telah mengatur lokasi di profil mereka.
    """
    # 1. Ambil profil penjual untuk mendapatkan lokasi
    seller_profile = db.query(Profile).filter(Profile.id == current_user.id).first()
    if not seller_profile:
        raise HTTPException(status_code=404, detail="Seller profile not found.")

    # 2. Validasi: Penjual harus punya lokasi
    if not seller_profile.location:
        raise HTTPException(
            status_code=400,
            detail="Please set your location in your profile before creating a listing."
        )

    # 3. Validasi input data
    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")
    if stock_quantity <= 0:
        raise HTTPException(status_code=400, detail="Stock quantity must be greater than 0")

    # 4. Unggah gambar ke Azure dan dapatkan URL-nya (permanen)
    try:
        image_urls = azure_storage.upload_images_to_blob(images)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 5. Buat objek Listing baru
    new_listing = Listing(
        title=title,
        description=description,
        price=price,
        unit=unit,
        stock_quantity=stock_quantity,
        seller_id=current_user.id,
        location=seller_profile.location,  # Warisi lokasi dari profil penjual
        image_urls=image_urls
    )

    # 6. Simpan ke database
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    return new_listing

@router.get("/nearby", response_model=LapakListResponse)
def get_lapak_nearby(
    lat: float = Query(..., description="Latitude of the user's location"),
    lon: float = Query(..., description="Longitude of the user's location"),
    radius: int = Query(5000, description="Radius in meters", gt=0),  # Default 5km
    db: Session = Depends(get_db)
):
    """
    Menemukan "Lapak Warga" yang tersedia di sekitar lokasi tertentu.
    Ini adalah endpoint utama untuk penemuan produk.
    """
    # 1. Buat titik geografi dari input lat/lon pengguna
    # Formatnya adalah 'POINT(longitude latitude)'
    user_location = WKTElement(f'POINT({lon} {lat})', srid=4326)

    # 2. Query ke database
    #    - Filter berdasarkan status 'available'
    #    - Gunakan func.ST_DWithin untuk mencari lokasi dalam radius tertentu.
    #    - Gunakan options(selectinload(Listing.seller)) untuk Eager Loading
    listings = (
        db.query(Listing)
        .options(selectinload(Listing.seller))  # <- Ini adalah optimasi penting!
        .filter(Listing.status == 'available')
        .filter(func.ST_DWithin(Listing.location, user_location, radius))
        .order_by(func.ST_Distance(Listing.location, user_location))  # Urutkan dari yang terdekat
        .all()
    )
    
    return {"items": listings}

@router.get("/{listing_id}", response_model=LapakSchema)
def get_lapak_detail(listing_id: str, db: Session = Depends(get_db)):
    """
    Mendapatkan detail lapak berdasarkan ID.
    """
    listing = (
        db.query(Listing)
        .options(selectinload(Listing.seller))
        .filter(Listing.id == listing_id)
        .first()
    )
    
    if not listing:
        raise HTTPException(status_code=404, detail="Lapak not found")
    
    return listing

@router.put("/{listing_id}", response_model=LapakSchema)
def update_lapak(
    listing_id: uuid.UUID,
    lapak_update: LapakUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Memperbarui detail lapak. Hanya pemilik lapak yang bisa melakukan ini.
    """
    listing = (
        db.query(Listing)
        .options(selectinload(Listing.seller))
        .filter(Listing.id == listing_id)
        .first()
    )
    
    if not listing:
        raise HTTPException(status_code=404, detail="Lapak not found")
    
    # Convert current_user.id string to UUID for comparison
    current_user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    
    if listing.seller_id != current_user_uuid:
        raise HTTPException(status_code=403, detail="Not authorized to update this lapak")

    # Update hanya field yang diberikan (exclude_unset=True)
    update_data = lapak_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(listing, key, value)
    
    db.commit()
    db.refresh(listing)
    return listing 