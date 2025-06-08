import nest_asyncio
import uvicorn
from pyngrok import ngrok, conf # Import conf

def run_ngrok(app):
    
    nest_asyncio.apply()
    ngrok_auth_token = "2xtvcyBG1ZhkFjLaqlB6tRqC11O_3wohV7RpNXfeUsRsm6Hke" # <--- GANTI INI

    # Konfigurasi pyngrok dengan authtoken Anda
    ngrok.set_auth_token(ngrok_auth_token)

    # Buka tunnel ngrok ke port 8000
    public_url = ngrok.connect(8000)
    print(f"✅ API Anda sekarang dapat diakses secara publik melalui URL ini: {public_url}")

    # Jalankan server Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)