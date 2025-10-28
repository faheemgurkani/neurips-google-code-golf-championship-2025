#!/bin/bash
# Setup script for the pipeline

echo "Setting up Google Code Golf 2025 Pipeline..."

# Create necessary directories
mkdir -p pipeline/output pipeline/logs

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set up environment
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env and add your GROQ_API_KEY"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GROQ_API_KEY"
echo "2. Run: python run_pipeline.py --start 1 --end 10"
echo ""
echo "Note: Make sure you're in the parent directory (neurips-google-code-golf-championship-2025/)"

