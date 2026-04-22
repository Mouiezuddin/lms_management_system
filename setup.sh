#!/bin/bash
echo "========================================"
echo "  Library Management System - Setup"
echo "========================================"
echo

echo "[1/4] Installing dependencies..."
pip install -r requirements.txt || exit 1

echo
echo "[2/4] Running migrations..."
python manage.py migrate || exit 1

echo
echo "[3/4] Seeding demo data (users + books + transactions)..."
python manage.py seed_demo || exit 1

echo
echo "[4/4] Seeding 500 IT books..."
python manage.py seed_it_books || exit 1

echo
echo "========================================"
echo "  Setup complete!"
echo "  Run: python manage.py runserver"
echo "  Visit: http://127.0.0.1:8000"
echo
echo "  Login credentials:"
echo "    Admin:    admin / admin123"
echo "    Student:  student1 / student123"
echo "    Faculty:  faculty1 / faculty123"
echo "========================================"
