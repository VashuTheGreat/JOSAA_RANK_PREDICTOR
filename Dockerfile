FROM python:3.12-slim

WORKDIR /app

# Copy dependency files first (better caching)
COPY requirements.txt pyproject.toml ./

# Install system dependencies required by LightGBM
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir .

# Copy rest of the application
COPY . .

EXPOSE 7860

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]