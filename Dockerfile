# ------------------------------
#   StudySpot API Dockerfile
# ------------------------------

# --- Base image ---
    FROM python:3.11-slim

    # --- Set working directory ---
    WORKDIR /app
    
    # --- Install system dependencies (optional, helps with mysqlclient etc.) ---
    RUN apt-get update && apt-get install -y \
        build-essential \
        default-libmysqlclient-dev \
        && rm -rf /var/lib/apt/lists/*
    
    # --- Install Python dependencies ---
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # --- Copy the entire application ---
    COPY . .
    
    # --- Expose FastAPI port ---
    EXPOSE 8080
    
    # --- Conditional run command ---
    CMD if [ "$ENV" = "local" ]; then \
            echo "Running in LOCAL mode with autoreload"; \
            uvicorn main:app --host 0.0.0.0 --port 8080 --reload; \
        else \
            echo "Running in PRODUCTION mode"; \
            uvicorn main:app --host 0.0.0.0 --port 8080; \
        fi
    