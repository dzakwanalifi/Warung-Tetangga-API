# app/routers/borongan.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timezone
from decimal import Decimal
import uuid

from ..core.database import get_db
from ..models.group_buy import GroupBuy
from ..models.group_buy_participant import GroupBuyParticipant
from ..models.profile import Profile
from ..schemas.borongan import (
    BoronganSummarySchema, 
    BoronganListResponse, 
    BoronganDetailSchema,
    BoronganCreate,
    ParticipantSchema,
    BoronganJoin,
    BoronganJoinResponse
)
from ..core.dependencies import get_current_user
from ..services import tripay as tripay_service

router = APIRouter()

@router.get("/", response_model=BoronganListResponse)
def get_active_borongan(db: Session = Depends(get_db)):
    """Get all active group buying sessions"""
    active_borongan = db.query(GroupBuy).filter(
        GroupBuy.status == 'active',
        GroupBuy.deadline > datetime.now(timezone.utc)
    ).all()
    
    borongan_list = []
    for borongan in active_borongan:
        participants_count = db.query(GroupBuyParticipant).filter(
            GroupBuyParticipant.group_buy_id == borongan.id
        ).count()
        
        total_ordered = db.query(GroupBuyParticipant).filter(
            GroupBuyParticipant.group_buy_id == borongan.id
        ).with_entities(func.sum(GroupBuyParticipant.quantity_ordered)).scalar() or 0
        
        borongan_summary = BoronganSummarySchema(
            id=borongan.id,
            title=borongan.title,
            description=borongan.description,
            price_per_unit=borongan.price_per_unit,
            unit=borongan.unit,
            target_quantity=borongan.target_quantity,
            current_quantity=total_ordered,
            participants_count=participants_count,
            deadline=borongan.deadline,
            pickup_point_address=borongan.pickup_point_address,
            status=borongan.status,
            created_at=borongan.created_at
        )
        borongan_list.append(borongan_summary)
    
    return BoronganListResponse(borongan=borongan_list)

@router.post("/", response_model=BoronganDetailSchema)
def create_borongan(
    borongan_data: BoronganCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new group buying session"""
    new_borongan = GroupBuy(
        title=borongan_data.title,
        description=borongan_data.description,
        price_per_unit=borongan_data.price_per_unit,
        unit=borongan_data.unit,
        target_quantity=borongan_data.target_quantity,
        deadline=borongan_data.deadline,
        pickup_point_address=borongan_data.pickup_point_address,
        supplier_id=current_user.id,
        status='active'
    )
    
    db.add(new_borongan)
    db.commit()
    db.refresh(new_borongan)
    
    # Return the created borongan with empty participants list
    return BoronganDetailSchema(
        id=new_borongan.id,
        supplier_id=new_borongan.supplier_id,
        title=new_borongan.title,
        description=new_borongan.description,
        price_per_unit=new_borongan.price_per_unit,
        unit=new_borongan.unit,
        target_quantity=new_borongan.target_quantity,
        current_quantity=0,
        participants_count=0,
        participants=[],
        deadline=new_borongan.deadline,
        pickup_point_address=new_borongan.pickup_point_address,
        status=new_borongan.status,
        created_at=new_borongan.created_at
    )

@router.get("/{borongan_id}", response_model=BoronganDetailSchema)
def get_borongan_detail(borongan_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific group buying session"""
    borongan = db.query(GroupBuy).filter(GroupBuy.id == borongan_id).first()
    
    if not borongan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group buying session not found"
        )
    
    participants = db.query(GroupBuyParticipant).filter(
        GroupBuyParticipant.group_buy_id == borongan_id
    ).all()
    
    participants_list = []
    total_ordered = 0
    
    for participant in participants:
        participants_list.append(ParticipantSchema(
            user_id=participant.user_id,
            full_name=participant.full_name,
            quantity_ordered=participant.quantity_ordered
        ))
        total_ordered += participant.quantity_ordered
    
    return BoronganDetailSchema(
        id=borongan.id,
        supplier_id=borongan.supplier_id,
        title=borongan.title,
        description=borongan.description,
        price_per_unit=borongan.price_per_unit,
        unit=borongan.unit,
        target_quantity=borongan.target_quantity,
        current_quantity=total_ordered,
        participants_count=len(participants_list),
        participants=participants_list,
        deadline=borongan.deadline,
        pickup_point_address=borongan.pickup_point_address,
        status=borongan.status,
        created_at=borongan.created_at
    )

@router.post("/{group_buy_id}/join", response_model=BoronganJoinResponse)
def join_borongan(
    group_buy_id: uuid.UUID,
    join_data: BoronganJoin,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mengizinkan pengguna yang login untuk bergabung dalam sesi borongan dengan integrasi Tripay.
    """
    # Gunakan .with_for_update() untuk mengunci baris group_buy selama transaksi
    # Ini mencegah kondisi race condition jika dua orang join bersamaan.
    borongan = db.query(GroupBuy).filter(GroupBuy.id == group_buy_id).with_for_update().first()

    # --- Validasi Bisnis ---
    if not borongan:
        raise HTTPException(status_code=404, detail="Group buy session not found.")
    if borongan.status != 'active':
        raise HTTPException(status_code=400, detail="This group buy is no longer active.")
    if borongan.deadline <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="The deadline for this group buy has passed.")
    if borongan.supplier_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot join a group buy that you created.")

    # Cek apakah user sudah join sebelumnya
    existing_participant = db.query(GroupBuyParticipant).filter(
        GroupBuyParticipant.group_buy_id == group_buy_id,
        GroupBuyParticipant.user_id == current_user.id
    ).first()
    if existing_participant:
        raise HTTPException(status_code=400, detail="You have already joined this group buy.")

    # Cek sisa kuota
    remaining_quantity = borongan.target_quantity - borongan.current_quantity
    if join_data.quantity_ordered > remaining_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot order that many. Only {remaining_quantity} unit(s) left to reach target."
        )

    # --- Logika Inti ---
    
    # 1. Hitung total harga
    total_price = borongan.price_per_unit * Decimal(join_data.quantity_ordered)

    # 2. Buat entri partisipan baru dengan status pending payment
    new_participant = GroupBuyParticipant(
        group_buy_id=group_buy_id,
        user_id=current_user.id,
        quantity_ordered=join_data.quantity_ordered,
        total_price=total_price,
        payment_status='pending'  # Status pending sampai payment dikonfirmasi
    )
    
    # 3. Update kuantitas saat ini di borongan
    borongan.current_quantity += join_data.quantity_ordered

    # 4. Cek apakah target tercapai
    if borongan.current_quantity >= borongan.target_quantity:
        borongan.status = 'successful'  # Ubah status jika target tercapai

    # 5. Simpan partisipan dan borongan ke database terlebih dahulu
    try:
        db.add(new_participant)
        db.add(borongan)
        db.commit()
        db.refresh(new_participant)
        db.refresh(borongan)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {e}")

    # --- Integrasi Tripay ---
    try:
        # Dapatkan profil user untuk nama lengkap
        user_profile = db.query(Profile).filter(Profile.id == current_user.id).first()
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Buat transaksi di Tripay
        tripay_response = tripay_service.create_transaction(
            participant=new_participant, 
            user_profile=user_profile,
            user_email=current_user.email
        )

        # Cek apakah Tripay response sukses
        if not tripay_response.get("success", True):  # Default True jika tidak ada key 'success'
            # Jika gagal membuat transaksi, rollback partisipasi
            db.delete(new_participant)
            borongan.current_quantity -= join_data.quantity_ordered
            if borongan.current_quantity < borongan.target_quantity:
                borongan.status = 'active'
            db.commit()
            
            error_message = tripay_response.get('message', 'Unknown error from payment gateway')
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to create payment transaction: {error_message}"
            )

        # Simpan referensi Tripay ke database
        tripay_data = tripay_response.get("data", {})
        new_participant.tripay_reference_code = tripay_data.get("reference")
        db.commit()

        # Siapkan respons untuk frontend
        if borongan.status == 'successful':
            message = "Successfully joined! Target reached! Please complete the payment."
        else:
            message = "Successfully joined! Please complete the payment."

        return BoronganJoinResponse(
            message=message,
            payment_url=tripay_data.get("checkout_url", ""),
            group_buy_status=borongan.status
        )

    except HTTPException:
        # Re-raise HTTPException yang sudah dihandle
        raise
    except Exception as e:
        # Handle unexpected errors dalam Tripay integration
        print(f"Error during Tripay integration: {e}")
        
        # Rollback partisipasi jika ada error setelah commit
        try:
            db.delete(new_participant)
            borongan.current_quantity -= join_data.quantity_ordered
            if borongan.current_quantity < borongan.target_quantity:
                borongan.status = 'active'
            db.commit()
        except Exception as rollback_error:
            print(f"Error during rollback: {rollback_error}")
        
        raise HTTPException(
            status_code=500, 
            detail="An error occurred during payment processing. Please try again."
        ) 

# --- Background Task Functions ---

def process_expired_borongan(db: Session):
    """
    Fungsi yang akan dijalankan di latar belakang untuk memproses borongan yang kedaluwarsa.
    """
    now = datetime.now(timezone.utc)
    print(f"[{now}] Running background task: Checking for expired group buys...")
    
    # Cari borongan yang statusnya 'active' tapi deadline-nya sudah lewat
    expired_borongan = db.query(GroupBuy).filter(
        GroupBuy.status == 'active',
        GroupBuy.deadline <= now
    ).all()

    count = 0
    for borongan in expired_borongan:
        # Ubah status menjadi 'failed'
        borongan.status = 'failed'
        
        # Untuk MVP, kita hanya mengubah status borongan
        # Di produksi, di sini bisa ditambahkan logika untuk:
        # 1. Refund otomatis ke partisipan
        # 2. Kirim notifikasi ke supplier dan partisipan
        # 3. Update payment status di Tripay jika diperlukan
        
        print(f"Group buy '{borongan.title}' (ID: {borongan.id}) has expired and is now marked as 'failed'.")
        count += 1

    if count > 0:
        db.commit()
        print(f"Background task finished. Processed {count} expired group buys.")
    else:
        print("Background task finished. No expired group buys found.")

# --- Internal Endpoints ---

@router.post("/internal/trigger-deadline-check", include_in_schema=False)
def trigger_deadline_check(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Endpoint internal untuk memicu pengecekan borongan yang kedaluwarsa.
    
    Endpoint ini:
    - Tidak muncul di dokumentasi API (include_in_schema=False)
    - Menjalankan proses pengecekan deadline di background
    - Dapat dipanggil oleh cron job atau scheduler eksternal
    
    PENTING: Amankan endpoint ini di produksi dengan:
    - API key internal
    - IP whitelist
    - Atau akses hanya dari internal network
    """
    background_tasks.add_task(process_expired_borongan, db)
    return {
        "message": "Deadline check has been triggered in the background.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    } 