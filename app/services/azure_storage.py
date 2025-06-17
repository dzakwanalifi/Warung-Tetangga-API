# app/services/azure_storage.py

import uuid
from fastapi import UploadFile
from azure.storage.blob import BlobServiceClient, ContentSettings
from typing import List

from ..core.config import settings

def upload_images_to_blob(files: List[UploadFile]) -> List[str]:
    """
    Mengunggah beberapa file gambar ke Azure Blob Storage dan mengembalikan daftar URL-nya.
    
    Args:
        files: List of UploadFile objects containing image files
        
    Returns:
        List of image URLs from Azure Blob Storage
        
    Raises:
        ValueError: If upload fails
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        image_urls = []

        for file in files:
            # Validasi file type (optional, tapi good practice)
            if not file.content_type or not file.content_type.startswith('image/'):
                raise ValueError(f"File {file.filename} is not a valid image file")
            
            # Buat nama file yang unik untuk menghindari konflik
            file_extension = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'jpg'
            blob_name = f"{uuid.uuid4()}.{file_extension}"
            
            blob_client = blob_service_client.get_blob_client(
                container=settings.AZURE_STORAGE_CONTAINER_NAME, 
                blob=blob_name
            )
            
            # Reset file pointer ke awal (penting!)
            file.file.seek(0)
            
            # Baca isi file dan unggah dengan ContentSettings yang benar
            blob_client.upload_blob(
                file.file.read(), 
                blob_type="BlockBlob",
                content_settings=ContentSettings(content_type=file.content_type)
            )
            
            image_urls.append(blob_client.url)
            
        return image_urls

    except Exception as e:
        print(f"Error uploading to Azure Blob Storage: {e}")
        # Sebaiknya lempar exception khusus agar bisa ditangani di router
        raise ValueError(f"Failed to upload images: {e}")

def delete_image_from_blob(image_url: str) -> bool:
    """
    Menghapus gambar dari Azure Blob Storage berdasarkan URL.
    
    Args:
        image_url: URL gambar yang akan dihapus
        
    Returns:
        True if successful, False otherwise
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        
        # Extract blob name from URL
        blob_name = image_url.split('/')[-1]
        
        blob_client = blob_service_client.get_blob_client(
            container=settings.AZURE_STORAGE_CONTAINER_NAME, 
            blob=blob_name
        )
        
        blob_client.delete_blob()
        return True
        
    except Exception as e:
        print(f"Error deleting image from Azure Blob Storage: {e}")
        return False 