# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=cyberkids.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY cyberkids/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional packages for production
RUN pip install --no-cache-dir gunicorn whitenoise psycopg2-binary python-decouple

# Copy project
COPY cyberkids/ .

# Collect static files
RUN python manage.py collectstatic --noinput || echo "No static files to collect"

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "cyberkids.wsgi:application"]
