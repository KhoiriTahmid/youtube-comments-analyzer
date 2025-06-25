FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install git terlebih dahulu
RUN apt update && apt install -y git && rm -rf /var/lib/apt/lists/*

# Copy semua file ke image
COPY . .

# Install dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Expose port FastAPI
EXPOSE 8000

# Jalankan server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
