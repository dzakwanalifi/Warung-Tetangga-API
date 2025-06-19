from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, cast, String
from geoalchemy2 import WKTElement
from geoalchemy2.types import Geometry
from typing import List, Optional
from decimal import Decimal
import uuid

from ..core.database import get_db
from ..core.dependencies import get_current_user
from ..models.listing import Listing
from ..models.profile import Profile
from ..schemas.lapak import LapakCreate, LapakSchema, LapakListResponse, LapakUpdate
from ..services import azure_storage
from ..services.gemini import (
    analyze_image_from_file, 
    analyze_photo_comprehensive,
    analyze_multiple_photos,
    LapakAnalysisResult,
    EnhancedAnalysisResult
)

router = APIRouter()

@router.post("/analyze", response_model=EnhancedAnalysisResult, tags=["AI"])
def analyze_images(
    images: List[UploadFile] = File(...),
    current_user = Depends(get_current_user)
):
    """
    Menganalisis foto produk secara komprehensif termasuk:
    - Identifikasi produk dan saran harga
    - Evaluasi kualitas foto (pencahayaan, komposisi, fokus, dll)
    - Insights actionable untuk meningkatkan foto
    - Rekomendasi untuk meningkatkan penjualan
    - Support untuk single atau multiple foto (maksimal 5)
    """
    # Validasi minimal 1 foto
    if not images or len(images) == 0:
        raise HTTPException(status_code=400, detail="At least one image is required")
    
    # Validasi semua file adalah gambar
    for i, image in enumerate(images):
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail=f"File {i+1} must be an image"
            )
    
    # Batasi maksimal 5 foto untuk performa
    if len(images) > 5:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 5 images allowed per analysis"
        )
    
    try:
        # Jika hanya 1 foto, gunakan analyze_photo_comprehensive
        # Jika multiple foto, gunakan analyze_multiple_photos
        if len(images) == 1:
            analysis_result = analyze_photo_comprehensive(images[0])
        else:
            analysis_result = analyze_multiple_photos(images)
        
        return analysis_result
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in image analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze images")

@router.post("", status_code=status.HTTP_201_CREATED, response_model=LapakSchema)
def create_lapak(
    # Gunakan Form untuk data dan File untuk upload
    title: str = Form(...),
    description: Optional[str] = Form(None),
    price: Decimal = Form(...),
    unit: str = Form(...),
    stock_quantity: int = Form(...),
    latitude: Optional[float] = Form(None),  # Optional coordinates from frontend
    longitude: Optional[float] = Form(None),  # Optional coordinates from frontend
    images: List[UploadFile] = File(...),  # Terima file gambar
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Membuat postingan "Lapak Warga" baru dengan upload gambar.
    Pengguna harus sudah login dan telah mengatur lokasi di profil mereka.
    Dapat menerima koordinat latitude/longitude opsional untuk lokasi lapak yang spesifik.
    """
    # 1. Ambil profil penjual untuk mendapatkan lokasi default
    seller_profile = db.query(Profile).filter(Profile.id == current_user.id).first()
    if not seller_profile:
        raise HTTPException(status_code=404, detail="Seller profile not found.")

    # 2. Tentukan lokasi lapak - prioritaskan koordinat dari frontend jika tersedia
    lapak_location = None
    if latitude is not None and longitude is not None:
        # Gunakan koordinat dari frontend
        lapak_location = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
        print(f"Using frontend coordinates: lat={latitude}, lon={longitude}")
    elif seller_profile.location:
        # Fallback ke lokasi profil penjual
        lapak_location = seller_profile.location
        print(f"Using seller profile location")
    else:
        # Tidak ada lokasi yang tersedia
        raise HTTPException(
            status_code=400,
            detail="Please provide coordinates or set your location in your profile before creating a listing."
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

    # 5. Buat objek Listing baru dengan lokasi yang tepat
    new_listing = Listing(
        title=title,
        description=description,
        price=price,
        unit=unit,
        stock_quantity=stock_quantity,
        seller_id=current_user.id,
        location=lapak_location,  # Gunakan lokasi yang sudah ditentukan (dari frontend atau profil)
        image_urls=image_urls
    )

    # 6. Simpan ke database
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    # Manually query the full object to return with all derived fields
    created_lapak = get_lapak_detail(new_listing.id, db)

    print(f"Lapak created with ID: {new_listing.id}")
    return created_lapak

@router.get("/nearby", response_model=LapakListResponse)
def get_lapak_nearby(
    lat: float = Query(..., description="Latitude of the user's location"),
    lon: float = Query(..., description="Longitude of the user's location"),
    radius: int = Query(5000, description="Radius in meters", gt=0),  # Default 5km
    page: int = Query(1, description="Page number", gt=0),
    limit: int = Query(12, description="Items per page", gt=0, le=50),
    db: Session = Depends(get_db)
):
    """
    Menemukan "Lapak Warga" yang tersedia di sekitar lokasi tertentu.
    Ini adalah endpoint utama untuk penemuan produk.
    """
    user_location = WKTElement(f'POINT({lon} {lat})', srid=4326)

    # Modify query to explicitly get lat/lon and distance
    base_query = (
        db.query(
            Listing,
            func.ST_X(Listing.location.cast(Geometry)).label('longitude'),
            func.ST_Y(Listing.location.cast(Geometry)).label('latitude'),
            func.ST_Distance(Listing.location, user_location).label('distance')
        )
        .options(selectinload(Listing.seller))
        .filter(Listing.status == 'available')
        .filter(func.ST_DWithin(Listing.location, user_location, radius))
        .order_by(func.ST_Distance(Listing.location, user_location))
    )
    
    total = base_query.count()
    offset = (page - 1) * limit
    results = base_query.offset(offset).limit(limit).all()

    # Process results to combine Listing object with derived fields
    lapak_list = []
    for listing, lon, lat, dist in results:
        lapak_schema = LapakSchema.from_orm(listing)
        lapak_schema.longitude = lon
        lapak_schema.latitude = lat
        lapak_schema.distance = dist
        lapak_list.append(lapak_schema)

    return {
        "lapak": lapak_list,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/my", response_model=LapakListResponse)
def get_my_lapak(
    page: int = Query(1, description="Page number", gt=0),
    limit: int = Query(12, description="Items per page", gt=0, le=50),
    status: Optional[str] = Query(None, description="Filter by status: available, sold_out, inactive"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mendapatkan semua lapak milik user yang sedang login.
    Endpoint ini memungkinkan user melihat semua produk yang telah mereka buat.
    """
    current_user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
    
    base_query = (
        db.query(
            Listing,
            func.ST_X(Listing.location.cast(Geometry)).label('longitude'),
            func.ST_Y(Listing.location.cast(Geometry)).label('latitude')
        )
        .options(selectinload(Listing.seller))
        .filter(Listing.seller_id == current_user_uuid)
    )
    
    if status:
        base_query = base_query.filter(Listing.status == status)
    
    base_query = base_query.order_by(Listing.created_at.desc())
    
    total = base_query.count()
    offset = (page - 1) * limit
    results = base_query.offset(offset).limit(limit).all()
    
    lapak_list = []
    for listing, lon, lat in results:
        lapak_schema = LapakSchema.from_orm(listing)
        lapak_schema.longitude = lon
        lapak_schema.latitude = lat
        lapak_list.append(lapak_schema)
        
    return {
        "lapak": lapak_list,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/{listing_id}", response_model=LapakSchema)
def get_lapak_detail(listing_id: str, db: Session = Depends(get_db)):
    """
    Mendapatkan detail lapak berdasarkan ID.
    """
    result = (
        db.query(
            Listing,
            func.ST_X(Listing.location.cast(Geometry)).label('longitude'),
            func.ST_Y(Listing.location.cast(Geometry)).label('latitude')
        )
        .options(selectinload(Listing.seller))
        .filter(Listing.id == listing_id)
        .first()
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Lapak not found")
    
    listing, lon, lat = result
    lapak_schema = LapakSchema.from_orm(listing)
    lapak_schema.longitude = lon
    lapak_schema.latitude = lat
    
    return lapak_schema

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

@router.get("/debug/locations", tags=["Debug"])
def debug_lapak_locations(
    db: Session = Depends(get_db)
):
    """
    Debug endpoint to check location data of lapak items.
    Shows coordinates for all lapak items.
    """
    # Query all lapak with their seller information and extract coordinates
    query = """
    SELECT 
        l.id,
        l.title,
        l.status,
        p.full_name as seller_name,
        ST_X(l.location::geometry) as longitude,
        ST_Y(l.location::geometry) as latitude,
        ST_X(p.location::geometry) as seller_longitude,
        ST_Y(p.location::geometry) as seller_latitude
    FROM listings l
    JOIN profiles p ON l.seller_id = p.id
    ORDER BY l.created_at DESC
    LIMIT 20
    """
    
    result = db.execute(query)
    rows = result.fetchall()
    
    return {
        "total_lapak": len(rows),
        "lapak_locations": [
            {
                "id": str(row[0]),
                "title": row[1],
                "status": row[2],
                "seller_name": row[3],
                "lapak_coordinates": {
                    "longitude": float(row[4]) if row[4] else None,
                    "latitude": float(row[5]) if row[5] else None
                },
                "seller_coordinates": {
                    "longitude": float(row[6]) if row[6] else None,
                    "latitude": float(row[7]) if row[7] else None
                }
            }
            for row in rows
        ]
    }

@router.get("/debug/profiles", tags=["Debug"])
def debug_seller_profiles(
    db: Session = Depends(get_db)
):
    """
    Debug endpoint to check which sellers have location data set.
    """
    # Query all profiles that have created lapak items
    query = """
    SELECT DISTINCT
        p.id,
        p.full_name,
        ST_X(p.location::geometry) as longitude,
        ST_Y(p.location::geometry) as latitude,
        COUNT(l.id) as lapak_count
    FROM profiles p
    LEFT JOIN listings l ON p.id = l.seller_id
    WHERE l.id IS NOT NULL
    GROUP BY p.id, p.full_name, p.location
    ORDER BY lapak_count DESC
    """
    
    result = db.execute(query)
    rows = result.fetchall()
    
    profiles_with_location = []
    profiles_without_location = []
    
    for row in rows:
        profile_data = {
            "id": str(row[0]),
            "full_name": row[1],
            "coordinates": {
                "longitude": float(row[2]) if row[2] else None,
                "latitude": float(row[3]) if row[3] else None
            },
            "lapak_count": row[4]
        }
        
        if row[2] is not None and row[3] is not None:
            profiles_with_location.append(profile_data)
        else:
            profiles_without_location.append(profile_data)
    
    return {
        "total_sellers": len(rows),
        "sellers_with_location": len(profiles_with_location),
        "sellers_without_location": len(profiles_without_location),
        "profiles_with_location": profiles_with_location,
        "profiles_without_location": profiles_without_location
    }

@router.post("/debug/fix-locations", tags=["Debug"])
def fix_lapak_locations(
    default_lat: float = Query(-6.200000, description="Default latitude (Jakarta center)"),
    default_lon: float = Query(106.816666, description="Default longitude (Jakarta center)"),
    db: Session = Depends(get_db)
):
    """
    Emergency migration: Set default location for lapak items that don't have location data.
    This is a one-time fix for existing data.
    """
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point
    
    # 1. Find all lapak items without location
    query_find = """
    SELECT l.id, l.title, p.full_name as seller_name
    FROM listings l
    JOIN profiles p ON l.seller_id = p.id
    WHERE l.location IS NULL OR p.location IS NULL
    """
    
    result = db.execute(query_find)
    rows = result.fetchall()
    
    if not rows:
        return {
            "message": "No lapak items need location fixes",
            "fixed_count": 0
        }
    
    # 2. Create default location point
    default_location = from_shape(Point(default_lon, default_lat), srid=4326)
    
    # 3. Update profiles without location first
    update_profiles_query = """
    UPDATE profiles 
    SET location = ST_SetSRID(ST_MakePoint(%s, %s), 4326)
    WHERE id IN (
        SELECT DISTINCT l.seller_id 
        FROM listings l 
        JOIN profiles p ON l.seller_id = p.id 
        WHERE p.location IS NULL
    )
    """
    
    db.execute(update_profiles_query, (default_lon, default_lat))
    
    # 4. Update lapak items without location
    update_lapak_query = """
    UPDATE listings 
    SET location = ST_SetSRID(ST_MakePoint(%s, %s), 4326)
    WHERE location IS NULL
    """
    
    db.execute(update_lapak_query, (default_lon, default_lat))
    
    # 5. Update lapak items where seller doesn't have location
    update_lapak_from_profile_query = """
    UPDATE listings l
    SET location = p.location
    FROM profiles p
    WHERE l.seller_id = p.id 
    AND l.location IS NULL 
    AND p.location IS NOT NULL
    """
    
    db.execute(update_lapak_from_profile_query)
    
    db.commit()
    
    return {
        "message": f"Successfully fixed location data for {len(rows)} lapak items",
        "fixed_count": len(rows),
        "default_coordinates": {
            "latitude": default_lat,
            "longitude": default_lon
        },
        "fixed_items": [
            {
                "id": str(row[0]),
                "title": row[1],
                "seller_name": row[2]
            }
            for row in rows
        ]
    } 