"""
Automatic setup script for Library Management System.
Run: python setup.py
"""
import os
import sys
import subprocess


def run(command, description):
    print(f"\n>>> {description}...")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        sys.exit(1)
    print(f"✓ Done: {description}")


def main():
    print("=" * 50)
    print("  Library Management System - Auto Setup")
    print("=" * 50)

    # Ensure we're in the right directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    python = sys.executable

    run(f"{python} -m pip install -r requirements.txt", "Installing dependencies")
    run(f"{python} manage.py migrate", "Running database migrations")
    run(f"{python} manage.py seed_demo", "Seeding demo users, books & transactions")
    run(f"{python} manage.py seed_it_books", "Seeding 500 IT books")

    print("\n" + "=" * 50)
    print("  ✅ Setup complete!")
    print("  Run: python manage.py runserver")
    print("  Visit: http://127.0.0.1:8000")
    print()
    print("  Login credentials:")
    print("    Admin:    admin    / admin123")
    print("    Student:  student1 / student123")
    print("    Faculty:  faculty1 / faculty123")
    print("=" * 50)


if __name__ == "__main__":
    main()
