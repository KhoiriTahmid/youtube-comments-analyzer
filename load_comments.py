import subprocess
import json
from fastapi import BackgroundTasks, HTTPException

from db_services import db_connect, add_comments_bulk

# --- GANTI FUNGSI LAMA DENGAN VERSI SUBPROCESS INI ---
def get_video_comments(video_id: str, background_tasks: BackgroundTasks):

    command = [
        "python",
        "comment_worker.py",
        video_id,
    ]

    try:
        # Menjalankan perintah sebagai subprocess
        result = subprocess.run(
            command,
            capture_output=True, # Tangkap outputnya
            text=True,           # Output sebagai teks
            check=True,          # Lemparkan error jika script worker gagal
            timeout=120          # Timeout 2 menit untuk mencegah hang
        )

        # Membaca output (yang berupa string JSON) dari worker
        output_data = json.loads(result.stdout)
        background_tasks.add_task(add_comments_bulk, output_data)

        comments = [comment['text'] for comment in output_data]
        # Periksa jika worker mengembalikan pesan error
        if isinstance(output_data, dict) and 'error' in output_data:
            raise HTTPException(status_code=500, detail=f"Worker error: {output_data['error']}")

        return comments

    except subprocess.CalledProcessError as e:
        # Jika script worker mengembalikan non-zero exit code
        raise HTTPException(status_code=500, detail=f"Subprocess worker gagal: {e.stderr}")
    except FileNotFoundError:
        # Jika python atau comment_worker.py tidak ditemukan
        raise HTTPException(status_code=500, detail="Error: Pastikan 'comment_worker.py' ada di direktori yang sama.")
    except Exception as e:
        # Untuk error lainnya
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal saat memanggil subprocess: {str(e)}")
