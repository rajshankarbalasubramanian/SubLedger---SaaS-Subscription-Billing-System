FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for compilation and database links
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies first to leverage Docker cache layers
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the entire workspace application files
COPY . .

EXPOSE 8000

# Fire up live production runtime engine container instance via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
