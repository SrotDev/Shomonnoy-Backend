
# Use the official Python image with system dependencies for GDAL/PostGIS
FROM python:3.11-slim

# Install system dependencies for GDAL, PostGIS, PostgreSQL client, and build tools
RUN apt-get update && \
    apt-get install -y binutils libproj-dev gdal-bin postgis postgresql-client build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# (Optional) Collect static files if using whitenoise/staticfiles
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start server with automatic migrations
CMD ["sh", "-c", "python manage.py migrate && gunicorn shomonnoy.wsgi:application --bind 0.0.0.0:8000"]