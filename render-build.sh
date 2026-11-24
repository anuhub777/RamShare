#!/usr/bin/env bash
# Render Unified Build Script for RAMShare
# Builds the Vite React Frontend and installs FastAPI Backend dependencies

set -o errexit

echo "=========================================="
echo "  1/2 Building Frontend (React + Vite)    "
echo "=========================================="
cd frontend
npm install
npm run build
cd ..

echo "=========================================="
echo "  2/2 Installing Backend Dependencies     "
echo "=========================================="
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo "=========================================="
echo "  Build Completed Successfully!           "
echo "=========================================="
