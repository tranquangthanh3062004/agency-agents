FROM python:3.11-slim

WORKDIR /app

# Cài đặt dependencies
COPY agency-test-ui/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code và data agents
COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "agency-test-ui.main:app", "--host", "0.0.0.0", "--port", "8000"]

