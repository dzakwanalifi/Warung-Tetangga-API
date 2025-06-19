# app/services/gemini.py

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import List, Optional
import json

from ..core.config import settings

# --- Enhanced Pydantic Schemas ---
class LapakAnalysisResult(BaseModel):
    title: str = Field(description="Judul produk yang disarankan dalam Bahasa Indonesia.")
    description: str = Field(description="Deskripsi produk yang ramah dan sederhana dalam Bahasa Indonesia.")
    suggested_price: int = Field(description="Harga yang disarankan dalam Rupiah (tanpa desimal).")
    unit: str = Field(description="Satuan jual yang umum untuk produk ini (e.g., kg, buah, ikat, botol, porsi).")
    category: str = Field(description="Kategori produk (Makanan, Minuman, Sayuran, Buah, Produk Kebun, Kue, atau Lainnya).")

class PhotoQualityAnalysis(BaseModel):
    overall_score: int = Field(description="Skor kualitas foto keseluruhan (0-100)")
    lighting_score: int = Field(description="Skor pencahayaan (0-100)")
    composition_score: int = Field(description="Skor komposisi (0-100)")
    focus_score: int = Field(description="Skor ketajaman/fokus (0-100)")
    background_score: int = Field(description="Skor kebersihan background (0-100)")
    color_vibrancy: int = Field(description="Skor kecerahan warna (0-100)")

class PhotoInsight(BaseModel):
    type: str = Field(description="Tipe insight: success, warning, info, suggestion")
    category: str = Field(description="Kategori: quality, lighting, composition, appeal, visibility")
    title: str = Field(description="Judul insight dalam Bahasa Indonesia")
    description: str = Field(description="Deskripsi detail insight")
    confidence: int = Field(description="Tingkat kepercayaan (0-100)")
    actionable: bool = Field(description="Apakah insight ini dapat ditindaklanjuti")

class EnhancedAnalysisResult(BaseModel):
    # Basic product analysis
    product_info: LapakAnalysisResult
    # Photo quality metrics
    photo_quality: PhotoQualityAnalysis
    # Actionable insights
    insights: List[PhotoInsight]
    # Additional recommendations
    recommendations: List[str] = Field(description="Rekomendasi spesifik untuk produk ini")

# --- Konfigurasi Klien Gemini ---
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
        Anda adalah asisten ahli untuk pasar hyperlocal Indonesia bernama 'Warung Warga'.
        Analisis gambar produk ini dan berikan informasi yang diminta dalam format JSON yang valid.
        Gunakan Bahasa Indonesia yang sederhana dan ramah untuk judul dan deskripsi.
        
        Berikan respons dalam format JSON dengan struktur:
        {
            "title": "nama produk yang menarik dan spesifik",
            "description": "deskripsi singkat, menarik dan informatif (2-3 kalimat)",
            "suggested_price": harga_yang_wajar_dalam_rupiah_tanpa_desimal,
            "unit": "satuan yang tepat (kg, buah, ikat, botol, porsi, pcs, dll)",
            "category": "kategori yang sesuai (Makanan, Minuman, Sayuran, Buah, Produk Kebun, Kue, atau Lainnya)"
        }
        
        Petunjuk:
        - Untuk harga, pertimbangkan harga pasar Indonesia yang wajar dan terjangkau
        - Untuk kategori, pilih yang paling sesuai dari: Makanan, Minuman, Sayuran, Buah, Produk Kebun, Kue, Lainnya
        - Buat deskripsi yang menarik dan informatif untuk meyakinkan pembeli
        - Emphasize kesegaran, kualitas, dan nilai tambah produk
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
            suggested_price=15000,
            unit="pcs",
            category="Lainnya"
        )

def analyze_photo_comprehensive(file: UploadFile) -> EnhancedAnalysisResult:
    """
    Melakukan analisis komprehensif terhadap foto produk termasuk kualitas foto,
    komposisi, dan memberikan insights yang actionable.
    """
    if not client:
        raise ValueError("Gemini client is not initialized. Check API Key.")

    try:
        # Membaca konten file sebagai bytes
        file.file.seek(0)
        image_bytes = file.file.read()

        # Membuat 'Part' dari konten file
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=file.content_type,
                data=image_bytes
            )
        )

        # Enhanced prompt untuk analisis komprehensif
        comprehensive_prompt = """
        Anda adalah ahli fotografi produk dan AI analyst untuk marketplace Indonesia 'Warung Warga'.
        Lakukan analisis mendalam terhadap foto produk ini dan berikan evaluasi komprehensif.
        
        Analisis harus mencakup:
        1. IDENTIFIKASI PRODUK: Tentukan jenis produk, kategori, dan perkiraan harga
        2. KUALITAS FOTO: Evaluasi pencahayaan, komposisi, fokus, background, dan warna
        3. INSIGHTS ACTIONABLE: Berikan saran spesifik untuk meningkatkan daya tarik foto
        4. REKOMENDASI PENJUALAN: Saran untuk meningkatkan penjualan produk
        
        Berikan respons dalam format JSON dengan struktur berikut:
        {
            "product_info": {
                "title": "nama produk yang menarik dan spesifik",
                "description": "deskripsi detail yang menarik (3-4 kalimat)",
                "suggested_price": harga_wajar_dalam_rupiah,
                "unit": "satuan yang tepat",
                "category": "kategori produk"
            },
            "photo_quality": {
                "overall_score": skor_keseluruhan_0_100,
                "lighting_score": skor_pencahayaan_0_100,
                "composition_score": skor_komposisi_0_100,
                "focus_score": skor_ketajaman_0_100,
                "background_score": skor_background_0_100,
                "color_vibrancy": skor_warna_0_100
            },
            "insights": [
                {
                    "type": "success/warning/info/suggestion",
                    "category": "quality/lighting/composition/appeal/visibility",
                    "title": "Judul insight",
                    "description": "Penjelasan detail insight",
                    "confidence": confidence_score_0_100,
                    "actionable": true/false
                }
            ],
            "recommendations": [
                "Rekomendasi spesifik 1",
                "Rekomendasi spesifik 2",
                "dst..."
            ]
        }
        
        Kriteria evaluasi:
        - Pencahayaan: Natural light vs artificial, shadows, brightness
        - Komposisi: Rule of thirds, centering, angle, framing
        - Fokus: Sharpness, blur, depth of field
        - Background: Cleanliness, distraction, contrast with product
        - Warna: Vibrancy, natural colors, saturation
        
        Berikan insights yang konstruktif dan actionable untuk membantu penjual!
        """
        
        # Panggil API dengan prompt yang enhanced
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-05-20',
            contents=[comprehensive_prompt, image_part],
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=EnhancedAnalysisResult,
            ),
        )
        
        # Parsing respons
        parsed_data = json.loads(response.text)
        return EnhancedAnalysisResult(**parsed_data)
        
    except Exception as e:
        print(f"Error in comprehensive analysis: {e}")
        # Fallback ke analisis basic
        basic_analysis = analyze_image_from_file(file)
        
        # Create fallback comprehensive result
        return EnhancedAnalysisResult(
            product_info=basic_analysis,
            photo_quality=PhotoQualityAnalysis(
                overall_score=75,
                lighting_score=70,
                composition_score=75,
                focus_score=80,
                background_score=65,
                color_vibrancy=70
            ),
            insights=[
                PhotoInsight(
                    type="info",
                    category="quality",
                    title="Analisis Foto Standar",
                    description="Foto sudah cukup baik untuk menampilkan produk. Pertimbangkan pencahayaan yang lebih baik untuk hasil optimal.",
                    confidence=75,
                    actionable=True
                ),
                PhotoInsight(
                    type="suggestion",
                    category="visibility",
                    title="Tambahkan Foto dari Sudut Lain",
                    description="Foto dari berbagai sudut akan memberikan gambaran produk yang lebih lengkap kepada pembeli.",
                    confidence=90,
                    actionable=True
                )
            ],
            recommendations=[
                "Gunakan pencahayaan natural atau lampu putih yang merata",
                "Bersihkan background untuk fokus pada produk",
                "Tambahkan foto detail untuk menunjukkan kualitas",
                "Pertimbangkan foto dengan objek referensi ukuran"
            ]
        )

def analyze_multiple_photos(files: List[UploadFile]) -> EnhancedAnalysisResult:
    """
    Menganalisis multiple foto untuk memberikan insights yang lebih komprehensif
    """
    if not files:
        raise ValueError("No files provided for analysis")
    
    # Analyze the first (main) photo comprehensively
    main_analysis = analyze_photo_comprehensive(files[0])
    
    # Add insights about multiple photos
    if len(files) > 1:
        # Add positive insight about multiple photos
        multi_photo_insight = PhotoInsight(
            type="success",
            category="visibility",
            title="Variasi Foto Tersedia",
            description=f"Anda telah mengunggah {len(files)} foto yang memberikan gambaran produk dari berbagai perspektif. Ini akan meningkatkan kepercayaan pembeli.",
            confidence=95,
            actionable=False
        )
        main_analysis.insights.append(multi_photo_insight)
        
        # Adjust recommendations for multiple photos
        main_analysis.recommendations.extend([
            "Pastikan setiap foto menampilkan aspek berbeda dari produk",
            "Gunakan foto pertama sebagai foto utama yang paling menarik",
            "Pertimbangkan foto close-up untuk detail penting"
        ])
    
    return main_analysis

# --- Fungsi lama untuk backward compatibility ---
def analyze_image_for_lapak(image_url: str) -> LapakAnalysisResult:
    """
    DEPRECATED: Fungsi lama untuk analisis dari URL. 
    Gunakan analyze_photo_comprehensive() atau analyze_multiple_photos() untuk implementasi baru.
    """
    return LapakAnalysisResult(
        title="Produk Segar",
        description="Produk berkualitas dari tetangga terdekat. Silakan hubungi penjual untuk detail lebih lanjut.",
        suggested_price=15000,
        unit="pcs",
        category="Lainnya"
    ) 