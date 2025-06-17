from fastapi import APIRouter, Request, Header, HTTPException, status, Depends
from typing import Optional
import hmac
import hashlib
import json
import uuid
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_db
from ..models.group_buy_participant import GroupBuyParticipant
from ..models.group_buy import GroupBuy
from ..schemas.payment import PaymentStatusResponse
from ..services import tripay as tripay_service

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

def validate_tripay_callback(request_body: bytes, x_callback_signature: Optional[str] = Header(None)):
    """Validasi signature dari callback Tripay."""
    if not x_callback_signature:
        raise HTTPException(status_code=401, detail="Missing callback signature")

    private_key = settings.TRIPAY_PRIVATE_KEY
    signature = hmac.new(
        bytes(private_key, 'latin-1'),
        request_body,
        hashlib.sha256
    ).hexdigest()

    if signature != x_callback_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

@router.post("/tripay/webhook")
async def tripay_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Menerima notifikasi pembayaran (webhook/callback) dari Tripay.
    SEKARANG DENGAN LOGIKA ROLLBACK DAN PENCEGAHAN RACE CONDITION.
    """
    try:
        # Ambil raw body request
        raw_body = await request.body()
        
        # 1. Validasi Signature
        validate_tripay_callback(raw_body, request.headers.get("x-callback-signature"))

        # 2. Parse JSON data
        try:
            data = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # 3. Ekstrak data penting
        payment_status = data.get("status")
        merchant_ref = data.get("merchant_ref")  # Ini adalah ID partisipasi kita
        reference = data.get("reference")  # Reference code dari Tripay
        
        print(f"Received Tripay webhook: status={payment_status}, merchant_ref={merchant_ref}, reference={reference}")

        if not merchant_ref:
            raise HTTPException(status_code=400, detail="Merchant reference not found in callback")

        # 4. Ambil partisipan dengan row-level locking untuk mencegah race condition
        participant = (
            db.query(GroupBuyParticipant)
            .filter(GroupBuyParticipant.id == merchant_ref)
            .with_for_update()  # Kunci baris partisipan
            .first()
        )

        if not participant:
            print(f"Participant with ID {merchant_ref} not found. Ignoring webhook.")
            return {"success": True, "message": "Participant not found, ignoring"}

        # 5. Simpan status lama untuk logging
        old_status = participant.payment_status

        # --- Logika Inti dengan Rollback yang Lebih Robust ---
        if payment_status == "PAID":
            # Jika status sudah 'paid', tidak perlu melakukan apa-apa lagi
            if participant.payment_status != "paid":
                participant.payment_status = "paid"
                print(f"Payment for participant {participant.id} confirmed as PAID.")
                db.add(participant)
                db.commit()
            else:
                print(f"Payment for participant {participant.id} already marked as PAID. Ignoring.")

        elif payment_status in ["EXPIRED", "FAILED", "CANCELED"]:
            # Hanya lakukan rollback jika status sebelumnya BUKAN 'failed'
            # untuk mencegah rollback ganda
            if participant.payment_status != "failed":
                print(f"Payment for participant {participant.id} {payment_status}. Rolling back quantity...")
                participant.payment_status = "failed"
                
                # Cari borongan terkait dengan row-level locking
                group_buy = (
                    db.query(GroupBuy)
                    .filter(GroupBuy.id == participant.group_buy_id)
                    .with_for_update()  # Kunci juga baris group_buy
                    .first()
                )

                if group_buy:
                    # Kembalikan kuantitas yang dipesan
                    group_buy.current_quantity -= participant.quantity_ordered
                    
                    # Jika borongan sebelumnya 'successful' karena partisipan ini,
                    # kembalikan statusnya ke 'active'
                    if group_buy.status == 'successful' and group_buy.current_quantity < group_buy.target_quantity:
                        group_buy.status = 'active'
                        print(f"Group buy {group_buy.id} status reverted to 'active'.")

                    db.add(group_buy)
                    print(f"Rolled back {participant.quantity_ordered} units from group buy {group_buy.id}. New quantity: {group_buy.current_quantity}")
                
                # Simpan participant dengan status failed
                db.add(participant)
                
                # Commit semua perubahan (participant status dan group_buy quantity) dalam satu transaksi
                db.commit()
            else:
                print(f"Payment for participant {participant.id} already marked as failed. Ignoring duplicate webhook.")
            
        elif payment_status == "UNPAID":
            if participant.payment_status != "pending":
                participant.payment_status = "pending"
                db.add(participant)
                db.commit()
                print(f"Payment for participant {participant.id} is still UNPAID.")
            else:
                print(f"Payment for participant {participant.id} already marked as UNPAID/pending.")
        else:
            print(f"Unknown payment status '{payment_status}' for participant {participant.id}. Ignoring.")
        
        print(f"Updated participant {participant.id} payment status from {old_status} to {participant.payment_status}")

        return {
            "success": True, 
            "message": f"Webhook processed successfully. Status updated to {participant.payment_status}"
        }

    except HTTPException:
        # Re-raise HTTPException yang sudah dihandle
        raise
    except Exception as e:
        # Log error dan return success agar Tripay tidak retry
        print(f"Error processing Tripay webhook: {e}")
        # Rollback transaction jika ada error
        db.rollback()
        return {
            "success": True, 
            "message": "Webhook received but processing failed. Please check logs."
        }

@router.get("/tripay/status/{participant_id}")
def check_payment_status(participant_id: str, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengecek status pembayaran partisipan.
    Bisa digunakan oleh frontend untuk polling status pembayaran.
    """
    participant = db.query(GroupBuyParticipant).filter(
        GroupBuyParticipant.id == participant_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return {
        "participant_id": participant.id,
        "payment_status": participant.payment_status,
        "tripay_reference": participant.tripay_reference_code,
        "total_price": participant.total_price,
        "group_buy_id": participant.group_buy_id
    }

@router.get("/methods")
def get_payment_methods():
    """
    Endpoint untuk mendapatkan daftar metode pembayaran yang tersedia dari Tripay.
    """
    try:
        result = tripay_service.get_payment_channels()
        if result.get("success"):
            return {
                "success": True,
                "data": result.get("data", [])
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to fetch payment methods: {result.get('message', 'Unknown error')}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch payment methods: {str(e)}"
        )

@router.get("/status/{participant_id}", response_model=PaymentStatusResponse)
def get_payment_status(participant_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengecek status pembayaran partisipan dengan sinkronisasi ke Tripay.
    Mengambil data terbaru dari Tripay jika ada tripay_reference_code.
    """
    # Cari partisipan di database
    participant = db.query(GroupBuyParticipant).filter(
        GroupBuyParticipant.id == str(participant_id)
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    tripay_status = None
    tripay_reference = participant.tripay_reference_code
    
    # Jika ada reference code, sinkronisasi dengan Tripay
    if tripay_reference:
        try:
            transaction_result = tripay_service.get_transaction_detail(tripay_reference)
            if transaction_result.get("success"):
                transaction_data = transaction_result.get("data", {})
                tripay_status = transaction_data.get("status")
                
                # Update status lokal jika berbeda dengan Tripay
                if tripay_status == "PAID" and participant.payment_status != "paid":
                    participant.payment_status = "paid"
                    db.add(participant)
                    db.commit()
                elif tripay_status in ["EXPIRED", "FAILED", "CANCELED"] and participant.payment_status not in ["failed", "expired"]:
                    participant.payment_status = "failed"
                    db.add(participant)
                    db.commit()
                
        except Exception as e:
            # Jika gagal mengambil dari Tripay, gunakan status lokal
            print(f"Failed to sync with Tripay for reference {tripay_reference}: {e}")
    
    return PaymentStatusResponse(
        participant_id=str(participant.id),
        payment_status=participant.payment_status,
        tripay_status=tripay_status,
        tripay_reference=tripay_reference
    ) 