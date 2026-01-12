FROM python:3.13-slim

WORKDIR /usr/src/app

# Copy and install dependencies first (for caching)
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy your app code
COPY . .

# Expose the port your Django app runs on
EXPOSE 8000

# Run migrations and start Gunicorn server (production-ready)
CMD ["sh", "-c", "python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:8000"]