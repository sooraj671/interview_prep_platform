#!/bin/bash

# Interview Preparation Platform - Setup Script
# This script sets up the development environment

echo "🚀 Setting up Interview Preparation Platform..."

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your configuration."
fi

# Run database migrations (if alembic is configured)
if [ -f "alembic.ini" ]; then
    echo "🗄️ Running database migrations..."
    alembic upgrade head
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env file with your database and API credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python main.py"
echo ""
echo "📚 API Documentation will be available at: http://localhost:8000/docs"
