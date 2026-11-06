FROM python:3.11-slim

WORKDIR /app

# Cài đặt dependencies
COPY agency-test-ui/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code và các folder agents vào image
COPY . .

# Biến môi trường PORT động (Tương thích Render, Railway, Fly.io, HuggingFace, Local)
ENV PORT=8000
EXPOSE 8000

# Khởi chạy qua shell để nhận diện biến $PORT được cấp phát động từ Cloud
CMD ["sh", "-c", "python -m uvicorn agency-test-ui.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
