# startup.sh

# Perintah untuk menjalankan aplikasi FastAPI dengan Gunicorn
# -w 4: Menggunakan 4 proses worker (sesuaikan dengan App Service Plan Anda)
# -k uvicorn.workers.UvicornWorker: Menggunakan worker Uvicorn yang kompatibel dengan ASGI
# app.main:app: Menunjuk ke instance 'app' di dalam file 'app/main.py'
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app