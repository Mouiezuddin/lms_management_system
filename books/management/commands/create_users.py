"""
Management command to create admin and student users.
Run: python manage.py create_users
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates admin and student users for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating users...')

        # Create Admin User
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                password='admin123',
                first_name='Admin',
                last_name='User',
                email='admin@library.com',
                role=User.Role.ADMIN,
            )
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Admin user created'))
        else:
            # Update existing admin to ensure proper permissions
            admin = User.objects.get(username='admin')
            admin.is_staff = True
            admin.is_superuser = True
            admin.role = User.Role.ADMIN
            admin.save()
            self.stdout.write(self.style.WARNING('  ⚠ Admin user already exists (updated permissions)'))

        # Create Student User
        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user(
                username='student',
                password='student123',
                first_name='John',
                last_name='Doe',
                email='student@university.edu',
                role=User.Role.STUDENT,
            )
            student.is_staff = False
            student.is_superuser = False
            student.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Student user created'))
        else:
            # Update existing student to ensure no admin access
            student = User.objects.get(username='student')
            student.is_staff = False
            student.is_superuser = False
            student.role = User.Role.STUDENT
            student.save()
            self.stdout.write(self.style.WARNING('  ⚠ Student user already exists (updated permissions)'))

        self.stdout.write(self.style.SUCCESS('\n✅ Users created successfully!\n'))
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:    username=admin      password=admin123')
        self.stdout.write('  Student:  username=student    password=student123')
