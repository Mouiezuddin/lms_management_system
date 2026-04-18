"""
Management command to create test overdue books and fines for testing.
Run: python manage.py create_test_overdue
"""
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from books.models import Book
from transactions.models import BookIssue


class Command(BaseCommand):
    help = 'Creates test overdue books and fines for the student user'

    def handle(self, *args, **options):
        self.stdout.write('Creating test overdue books and fines...')

        # Get student user
        try:
            student = User.objects.get(username='student')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Student user not found. Please create it first.'))
            return

        # Get admin user
        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin = None

        # Get some books
        books = Book.objects.filter(available_quantity__gt=0)[:3]
        
        if not books:
            self.stdout.write(self.style.ERROR('No books available. Please add books first.'))
            return

        # Create overdue issues
        today = datetime.date.today()
        
        # Issue 1: 5 days overdue (still active)
        if books[0].available_quantity > 0:
            issue1 = BookIssue(
                user=student,
                book=books[0],
                issue_date=today - datetime.timedelta(days=12),
                due_date=today - datetime.timedelta(days=5),
                issued_by=admin,
            )
            issue1.save()
            books[0].available_quantity -= 1
            books[0].save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created overdue issue: {books[0].title} (5 days late, ₹25 fine)'))

        # Issue 2: 3 days overdue (still active)
        if len(books) > 1 and books[1].available_quantity > 0:
            issue2 = BookIssue(
                user=student,
                book=books[1],
                issue_date=today - datetime.timedelta(days=10),
                due_date=today - datetime.timedelta(days=3),
                issued_by=admin,
            )
            issue2.save()
            books[1].available_quantity -= 1
            books[1].save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created overdue issue: {books[1].title} (3 days late, ₹15 fine)'))

        # Issue 3: Returned late with pending fine
        if len(books) > 2 and books[2].available_quantity > 0:
            issue3 = BookIssue(
                user=student,
                book=books[2],
                issue_date=today - datetime.timedelta(days=20),
                due_date=today - datetime.timedelta(days=13),
                return_date=today - datetime.timedelta(days=5),
                fine_amount=40,  # 8 days late × ₹5
                fine_status=BookIssue.FineStatus.PENDING,
                issued_by=admin,
            )
            issue3.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created returned book with pending fine: {books[2].title} (₹40 fine)'))

        self.stdout.write(self.style.SUCCESS('\n✅ Test data created successfully!'))
        self.stdout.write('Now login as student (username: student, password: student123) to see the notifications.')
