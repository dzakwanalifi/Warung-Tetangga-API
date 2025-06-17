# app/services/gemini.py

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from fastapi import UploadFile  # Impor UploadFile untuk type hinting
import json

from ..core.config import settings

# --- Pydantic Schema untuk output yang diinginkan dari AI ---
class LapakAnalysisResult(BaseModel):
    title: str = Field(description="Judul produk yang disarankan dalam Bahasa Indonesia.")
    description: str = Field(description="Deskripsi produk yang ramah dan sederhana dalam Bahasa Indonesia.")
    unit: str = Field(description="Satuan jual yang umum untuk produk ini (e.g., kg, buah, ikat, botol, porsi).")

# --- Konfigurasi Klien Gemini ---
# Menggunakan API Key dari environment variables yang sudah di-load oleh config.py
# Tidak perlu mengkonfigurasi ulang, karena library ini juga mencari env var GOOGLE_API_KEY
# Namun, untuk eksplisit, kita akan inisialisasi dengan Client()
try:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    print(f"Failed to initialize Gemini Client: {e}")
    client = None

def analyze_image_from_file(file: UploadFile) -> LapakAnalysisResult:
    """
    Menganalisis file gambar yang diunggah langsung menggunakan Gemini 1.5 Flash
    dan mengembalikan hasilnya dalam format JSON yang terstruktur.
    """
    if not client:
        raise ValueError("Gemini client is not initialized. Check API Key.")

    try:
        # Membaca konten file sebagai bytes
        file.file.seek(0)  # Reset file pointer ke awal
        image_bytes = file.file.read()

        # Membuat 'Part' dari konten file langsung
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=file.content_type,  # Gunakan mime_type dari UploadFile
                data=image_bytes
            )
        )

        # Membuat prompt teks
        text_prompt = """
        Anda adalah asisten ahli untuk pasar hyperlocal Indonesia bernama 'Warung Tetangga'.
        Analisis gambar produk ini dan berikan informasi yang diminta dalam format JSON yang valid.
        Gunakan Bahasa Indonesia yang sederhana dan ramah untuk judul dan deskripsi.
        
        Berikan respons dalam format JSON dengan struktur:
        {
            "title": "nama produk yang menarik",
            "description": "deskripsi singkat dan menarik",
            "unit": "satuan yang tepat (kg, buah, ikat, botol, porsi, dll)"
        }
        """
        
        # Panggil API dengan part gambar
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-05-20',
            contents=[text_prompt, image_part],
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=LapakAnalysisResult,
            ),
        )
        
        # Parsing respons
        parsed_data = json.loads(response.text)
        return LapakAnalysisResult(**parsed_data)
        
    except Exception as e:
        print(f"Error calling Gemini API with file content: {e}")
        # Fallback: return a default analysis
        return LapakAnalysisResult(
            title="Produk Segar",
            description="Produk berkualitas dari tetangga terdekat. Silakan hubungi penjual untuk detail lebih lanjut.",
            unit="buah"
        )

# --- Fungsi lama untuk backward compatibility (akan dihapus nanti) ---
def analyze_image_for_lapak(image_url: str) -> LapakAnalysisResult:
    """
    DEPRECATED: Fungsi lama untuk analisis dari URL. 
    Gunakan analyze_image_from_file() untuk implementasi baru.
    """
    return LapakAnalysisResult(
        title="Produk Segar",
        description="Produk berkualitas dari tetangga terdekat. Silakan hubungi penjual untuk detail lebih lanjut.",
        unit="buah"
    ) 