#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Initializing database tables..."
python init_production_db.py

echo ""
echo "✅ Build complete!"
