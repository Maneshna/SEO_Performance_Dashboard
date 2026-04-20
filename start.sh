#!/bin/bash
# Quick start script for SEO Performance Dashboard

echo "🚀 Starting SEO Performance Dashboard..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Launch Streamlit
echo ""
echo "✅ Starting dashboard..."
echo "🌐 Opening at http://localhost:8501"
echo ""

streamlit run frontend/app.py
