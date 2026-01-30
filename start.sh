#!/bin/bash
# Quick start script for Unix/Linux/Mac

echo "=========================================="
echo "F.A.D. List Builder - Quick Start"
echo "=========================================="
echo ""

echo "[1/3] Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "[2/3] Initializing database..."
python init_db.py
echo ""

echo "[3/3] Starting application..."
echo ""
echo "The app will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
python app.py
