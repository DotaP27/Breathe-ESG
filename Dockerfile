FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal OS deps needed for some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Copy project
COPY . .

ENV PORT=8000

# Ensure commands run from the Django project directory where manage.py lives
WORKDIR /app/breathe_esg

# Run migrations, collectstatic then start Gunicorn
CMD bash -lc "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn breathe_esg.wsgi:application --bind 0.0.0.0:${PORT} --workers 3"
