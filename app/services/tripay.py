# app/services/tripay.py

import hmac
import hashlib
import time
import requests
from typing import Dict, Any
from decimal import Decimal

from ..core.config import settings
from ..models.group_buy_participant import GroupBuyParticipant
from ..models.profile import Profile

def create_transaction(participant: GroupBuyParticipant, user_profile: Profile, user_email: str) -> Dict[str, Any]:
    """
    Membuat transaksi baru di Tripay dan mengembalikan respons dari API.
    
    Args:
        participant: Instance GroupBuyParticipant yang berisi data pesanan
        user_profile: Profile pengguna untuk mendapatkan nama lengkap
        user_email: Email pengguna dari Supabase auth
    
    Returns:
        Dict dengan response dari Tripay API
    """
    try:
        # Data untuk request
        merchant_ref = str(participant.id)  # Gunakan ID partisipasi sebagai referensi unik
        amount = int(participant.total_price)  # Tripay memerlukan amount dalam integer (rupiah)

        # Membuat signature sesuai dokumentasi Tripay
        sign_str = f"{settings.TRIPAY_MERCHANT_CODE}{merchant_ref}{amount}"
        signature = hmac.new(
            bytes(settings.TRIPAY_PRIVATE_KEY, 'latin-1'),
            bytes(sign_str, 'latin-1'),
            hashlib.sha256
        ).hexdigest()

        # Payload yang akan dikirim ke Tripay
        payload = {
            'method': 'QRISC',  # QRIS sebagai metode pembayaran default
            'merchant_ref': merchant_ref,
            'amount': amount,
            'customer_name': user_profile.full_name,
            'customer_email': user_email,
            'customer_phone': '081234567890',  # Placeholder, bisa ditambahkan ke profile nanti
            'order_items': [
                {
                    'sku': str(participant.group_buy.id),
                    'name': participant.group_buy.title,
                    'price': int(participant.group_buy.price_per_unit),
                    'quantity': participant.quantity_ordered,
                }
            ],
            'expired_time': int(time.time() + (1 * 60 * 60)),  # Expired dalam 1 jam
            'signature': signature
        }

        headers = {
            "Authorization": f"Bearer {settings.TRIPAY_API_KEY}",
            "Content-Type": "application/json"
        }

        # Melakukan request ke API Tripay
        response = requests.post(
            f"{settings.TRIPAY_API_URL}/transaction/create",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()  # Raise error jika status code bukan 2xx
        
        response_data = response.json()
        
        # Log untuk debugging
        print(f"Tripay transaction created successfully for participant {participant.id}")
        print(f"Tripay response: {response_data}")
        
        return response_data

    except requests.exceptions.RequestException as e:
        # Handle error koneksi atau HTTP error dari Tripay
        error_msg = f"Error creating Tripay transaction: {e}"
        print(error_msg)
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Tripay Error Response: {error_detail}")
                return {
                    "success": False, 
                    "message": error_detail.get("message", str(e)),
                    "errors": error_detail.get("errors", [])
                }
            except:
                print(f"Tripay Response Text: {e.response.text}")
                return {"success": False, "message": e.response.text}
        
        return {"success": False, "message": str(e)}
    
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error in Tripay service: {e}"
        print(error_msg)
        return {"success": False, "message": error_msg}

def get_payment_channels() -> Dict[str, Any]:
    """
    Mengambil daftar channel pembayaran yang tersedia dari Tripay.
    """
    try:
        headers = {"Authorization": f"Bearer {settings.TRIPAY_API_KEY}"}
        response = requests.get(
            f"{settings.TRIPAY_API_URL}/merchant/payment-channel",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Tripay payment channels: {e}")
        return {"success": False, "message": str(e)}

def get_transaction_detail(reference: str) -> Dict[str, Any]:
    """
    Mengambil detail transaksi dari Tripay berdasarkan referensi.
    """
    try:
        headers = {"Authorization": f"Bearer {settings.TRIPAY_API_KEY}"}
        params = {"reference": reference}
        response = requests.get(
            f"{settings.TRIPAY_API_URL}/transaction/detail",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Tripay transaction detail for ref {reference}: {e}")
        return {"success": False, "message": str(e)}

def get_payment_methods() -> Dict[str, Any]:
    """
    Mendapatkan daftar metode pembayaran yang tersedia dari Tripay.
    Alias untuk get_payment_channels() untuk backward compatibility.
    
    Returns:
        Dict dengan daftar metode pembayaran
    """
    return get_payment_channels()

def check_transaction_status(reference: str) -> Dict[str, Any]:
    """
    Mengecek status transaksi berdasarkan reference code.
    Alias untuk get_transaction_detail() untuk backward compatibility.
    
    Args:
        reference: Reference code dari Tripay
    
    Returns:
        Dict dengan status transaksi
    """
    return get_transaction_detail(reference) 