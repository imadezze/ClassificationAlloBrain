#!/bin/bash

# Semantic Classifier - Quick Start Script

echo "🧠 Semantic Classifier - Starting..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if OPENAI_API_KEY is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "⚠️  OPENAI_API_KEY is not configured in .env"
    echo "   Please add your OpenAI API key to .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Run Streamlit
echo ""
echo "🚀 Launching Streamlit application..."
echo "   URL: http://localhost:8501"
echo ""
streamlit run app.py
