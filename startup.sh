#!/bin/bash
# Railway Startup Script
# Initializes database and starts the application

echo "🚀 Starting Interview Preparation Platform..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ Database is ready!"

# Initialize database schema
echo "🗄️ Initializing database schema..."
python scripts/init_railway_db.py

# Start the application
echo "🌟 Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
