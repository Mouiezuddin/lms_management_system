@echo off
echo ========================================
echo   Library Management System - Setup
echo ========================================
echo.

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo [2/4] Running migrations...
python manage.py migrate
if errorlevel 1 goto error

echo.
echo [3/4] Seeding demo data (users + books + transactions)...
python manage.py seed_demo
if errorlevel 1 goto error

echo.
echo [4/4] Seeding 500 IT books...
python manage.py seed_it_books
if errorlevel 1 goto error

echo.
echo ========================================
echo   Setup complete!
echo   Run: python manage.py runserver
echo   Visit: http://127.0.0.1:8000
echo.
echo   Login credentials:
echo     Admin:    admin / admin123
echo     Student:  student1 / student123
echo     Faculty:  faculty1 / faculty123
echo ========================================
goto end

:error
echo.
echo ERROR: Setup failed. Check the output above.
exit /b 1

:end
