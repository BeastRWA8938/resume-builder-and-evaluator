# Use official Python runtime as base image
FROM python:3.10-slim

# Prevent Python from writing pyc files to disc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for PDF/Docx text parsing and XeLaTeX resume compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-plain-generic \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Install Python package requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy project workspace files
COPY . /app

# Expose FastAPI development server port
EXPOSE 8000

# Set environment variables defaults
ENV ALLOWED_ORIGINS="*"
ENV DATABASE_PATH="/app/backend/resume_analyzer.db"

# Start FastAPI application using Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
