"""
Management command to seed the database with demo data.
Run: python manage.py seed_demo
"""
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from books.models import Book, Category
from transactions.models import BookIssue


class Command(BaseCommand):
    help = 'Seeds the database with demo data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # ── Categories ─────────────────────────────────────────────────────
        categories_data = [
            ('Computer Science', 'Programming, algorithms, data structures'),
            ('Mathematics', 'Pure and applied mathematics'),
            ('Physics', 'Classical and modern physics'),
            ('Literature', 'Fiction, non-fiction, classic literature'),
            ('History', 'World history and civilizations'),
            ('Engineering', 'Mechanical, electrical, civil engineering'),
        ]
        categories = {}
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
            categories[name] = cat
        self.stdout.write(f'  ✓ {len(categories)} categories created')

        # ── Books ───────────────────────────────────────────────────────────
        books_data = [
            ('Clean Code', 'Robert C. Martin', '9780132350884', 'Computer Science', 'Prentice Hall', 2008, 5),
            ('The Pragmatic Programmer', 'David Thomas', '9780201616224', 'Computer Science', 'Addison-Wesley', 1999, 3),
            ('Design Patterns', 'Gang of Four', '9780201633610', 'Computer Science', 'Addison-Wesley', 1994, 4),
            ('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 'Computer Science', 'MIT Press', 2009, 6),
            ('Python Crash Course', 'Eric Matthes', '9781593276034', 'Computer Science', 'No Starch Press', 2019, 8),
            ('Calculus', 'James Stewart', '9781285741550', 'Mathematics', 'Cengage', 2015, 10),
            ('Linear Algebra', 'Gilbert Strang', '9780980232714', 'Mathematics', 'Wellesley', 2016, 5),
            ('A Brief History of Time', 'Stephen Hawking', '9780553380163', 'Physics', 'Bantam', 1988, 4),
            ('Feynman Lectures on Physics', 'Richard Feynman', '9780465023820', 'Physics', 'Basic Books', 2011, 3),
            ('Pride and Prejudice', 'Jane Austen', '9780141439518', 'Literature', 'Penguin Classics', 2002, 7),
            ('To Kill a Mockingbird', 'Harper Lee', '9780061935466', 'Literature', 'HarperCollins', 2002, 5),
            ('Sapiens', 'Yuval Noah Harari', '9780062316097', 'History', 'Harper', 2015, 6),
            ('The Art of War', 'Sun Tzu', '9781599869773', 'History', 'Filiquarian', 2007, 4),
        ]
        books = []
        for title, author, isbn, cat_name, publisher, year, qty in books_data:
            book, _ = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': title,
                    'author': author,
                    'category': categories.get(cat_name),
                    'publisher': publisher,
                    'publication_year': year,
                    'total_quantity': qty,
                    'available_quantity': qty,
                }
            )
            books.append(book)
        self.stdout.write(f'  ✓ {len(books)} books created')

        # ── Users ───────────────────────────────────────────────────────────
        users_data = [
            ('admin', 'Admin', 'User', 'admin@library.com', User.Role.ADMIN, 'admin123'),
            ('student1', 'Alice', 'Johnson', 'alice@university.edu', User.Role.STUDENT, 'student123'),
            ('student2', 'Bob', 'Smith', 'bob@university.edu', User.Role.STUDENT, 'student123'),
            ('faculty1', 'Dr. Carol', 'Williams', 'carol@university.edu', User.Role.FACULTY, 'faculty123'),
            ('faculty2', 'Prof. David', 'Brown', 'david@university.edu', User.Role.FACULTY, 'faculty123'),
        ]
        created_users = {}
        for username, first, last, email, role, password in users_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first,
                    last_name=last,
                    email=email,
                    role=role,
                )
                created_users[username] = user
            else:
                created_users[username] = User.objects.get(username=username)
        self.stdout.write(f'  ✓ {len(created_users)} users created/found')

        # ── Sample Transactions ─────────────────────────────────────────────
        admin = created_users.get('admin')
        student1 = created_users.get('student1')
        student2 = created_users.get('student2')
        faculty1 = created_users.get('faculty1')

        if student1 and not BookIssue.objects.filter(user=student1).exists():
            # Active issue
            issue1, _ = BookIssue.issue_book(student1, books[0], issued_by=admin)
            # Overdue issue (manually set dates)
            if books[1].available_quantity > 0:
                issue2 = BookIssue(
                    user=student1,
                    book=books[1],
                    issue_date=datetime.date.today() - datetime.timedelta(days=14),
                    due_date=datetime.date.today() - datetime.timedelta(days=7),
                    issued_by=admin,
                )
                issue2.save()
                books[1].available_quantity -= 1
                books[1].save(update_fields=['available_quantity'])

        if student2 and not BookIssue.objects.filter(user=student2).exists():
            issue3, _ = BookIssue.issue_book(student2, books[4], issued_by=admin)
            # A returned book with fine
            if books[5].available_quantity > 0:
                issue4 = BookIssue(
                    user=student2,
                    book=books[5],
                    issue_date=datetime.date.today() - datetime.timedelta(days=20),
                    due_date=datetime.date.today() - datetime.timedelta(days=13),
                    return_date=datetime.date.today() - datetime.timedelta(days=3),
                    fine_amount=50,
                    fine_status=BookIssue.FineStatus.PENDING,
                    issued_by=admin,
                )
                issue4.save()
                # Note: qty not changed since it was already returned

        if faculty1 and not BookIssue.objects.filter(user=faculty1).exists():
            BookIssue.issue_book(faculty1, books[7], issued_by=admin)

        self.stdout.write('  ✓ Sample transactions created')
        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!\n'))
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:    username=admin        password=admin123')
        self.stdout.write('  Student:  username=student1     password=student123')
        self.stdout.write('  Faculty:  username=faculty1     password=faculty123')
