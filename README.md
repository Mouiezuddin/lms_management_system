# 📚 Library Management System — Django

A complete, production-ready Library Management System built with Django, featuring role-based access, book management, transaction tracking, and an automated fine system.

---

## 🗂️ Project Structure

```
lms/
├── library/                  # Django project (settings, root URLs, wsgi)
│   ├── settings.py
│   └── urls.py
├── accounts/                 # Custom user model + auth + dashboard
│   ├── models.py             # User (roles: Admin, Student, Faculty)
│   ├── views.py              # Login, Logout, Dashboard, UserCRUD
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── books/                    # Book catalog
│   ├── models.py             # Book, Category
│   ├── views.py              # BookListView, BookDetail, CRUD
│   ├── forms.py
│   ├── urls.py
│   └── management/commands/seed_demo.py
├── transactions/             # Issue / Return / Fine system
│   ├── models.py             # BookIssue (full business logic)
│   ├── views.py              # IssueBook, ReturnBook, Fines
│   ├── forms.py
│   └── urls.py
├── templates/
│   ├── base.html             # Sidebar layout, Bootstrap 5
│   ├── accounts/             # login, dashboard, user_list, user_form
│   ├── books/                # book_list, book_detail, book_form, categories
│   └── transactions/         # transaction_list, issue, return, detail, fines
├── static/
├── manage.py
└── requirements.txt
```

---

## ⚡ Quick Setup

### Step 1 — Clone & Create Virtual Environment

```bash
git clone https://github.com/Mouiezuddin/lms_management_system.git
cd lms_management_system

# Create virtual environment
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS / Linux
source venv/bin/activate
```

### Step 2 — One-Command Setup (installs deps + migrates + seeds all data)

**Windows:**
```bash
setup.bat
```

**macOS / Linux:**
```bash
chmod +x setup.sh && ./setup.sh
```

> ⚠️ **Important:** You MUST run the setup script (or the manual steps below) after cloning. The database is not included in the repo — the seed commands create all the demo data, users, and books.

---

### Manual Setup (alternative)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo        # creates users, categories, books, transactions
python manage.py seed_it_books    # adds 500 IT books
```

### Step 3 — Run Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

### Default Login Credentials

| Role    | Username | Password    |
|---------|----------|-------------|
| Admin   | admin    | admin123    |
| Student | student1 | student123  |
| Faculty | faculty1 | faculty123  |

---

## 🔐 Role Permissions

| Feature                  | Admin | Faculty | Student |
|--------------------------|-------|---------|---------|
| View book catalog        | ✅    | ✅      | ✅      |
| Search books             | ✅    | ✅      | ✅      |
| View own transactions    | ✅    | ✅      | ✅      |
| Add / Edit / Delete book | ✅    | ❌      | ❌      |
| Issue book to user       | ✅    | ❌      | ❌      |
| Process book return      | ✅    | ❌      | ❌      |
| View all transactions    | ✅    | ❌      | ❌      |
| Manage fines             | ✅    | ❌      | ❌      |
| Manage users             | ✅    | ❌      | ❌      |
| Django admin panel       | ✅    | ❌      | ❌      |

---

## 📐 Business Rules

| Rule                  | Value         |
|-----------------------|---------------|
| Loan period           | 7 days        |
| Max books per user    | 3             |
| Fine rate             | ₹5 per day    |
| Fine trigger          | return_date > due_date |

All rules are configurable in `library/settings.py`:
```python
FINE_RATE_PER_DAY = 5      # ₹ per late day
MAX_BOOKS_PER_USER = 3     # concurrent limit
LOAN_PERIOD_DAYS = 7       # due date offset
```

---

## 🧩 Key Design Decisions

### 1. Business Logic in Models, Not Views
All core logic (`issue_book`, `process_return`, `mark_fine_paid`, `waive_fine`) lives in `BookIssue` model as class/instance methods. Views just call these methods and handle HTTP responses.

### 2. Custom User Model
Extends `AbstractUser` with a `role` field (`ADMIN`, `STUDENT`, `FACULTY`). Defined early in the project to avoid migration issues later.

### 3. Fine System
Fine is calculated as a `@property` (`calculated_fine`) during an active loan, and stored as `fine_amount` on return. This prevents recalculation issues.

### 4. Signals (not needed — logic is explicit)
Django signals were considered but the explicit `issue_book()` and `process_return()` class methods provide cleaner error handling and make the flow obvious without hidden side effects.

### 5. Class-Based Views Throughout
All views use Django CBVs:
- `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`
- `FormView` for complex form flows (issue book)
- `View` for multi-step processes (return + fine)
- Custom `AdminRequiredMixin` for role-gating

---

## 🛠️ Django Admin

The Django admin panel is available at `/admin/` with full CRUD for all models:
- **Users** — manage roles, activate/deactivate
- **Books** — add/edit with all fields
- **Book Issues** — view all transactions
- **Categories** — manage book categories

---

## 🌐 URL Structure

```
/                               → Redirect to dashboard
/accounts/login/                → Login page
/accounts/logout/               → Logout (POST)
/accounts/dashboard/            → Dashboard (role-aware)
/accounts/users/                → User list (admin)
/accounts/users/create/         → Create user (admin)
/accounts/users/<pk>/edit/      → Edit user (admin)

/books/                         → Book catalog (with search)
/books/<pk>/                    → Book detail
/books/add/                     → Add book (admin)
/books/<pk>/edit/               → Edit book (admin)
/books/<pk>/delete/             → Delete book (admin)
/books/categories/              → Category list (admin)
/books/categories/add/          → Add category (admin)

/transactions/                  → All transactions (admin)
/transactions/mine/             → My issues (any user)
/transactions/issue/            → Issue book (admin)
/transactions/<pk>/             → Transaction detail
/transactions/<pk>/return/      → Return book (admin)
/transactions/<pk>/fine/        → Settle fine (admin)
/transactions/fines/            → Pending fines list (admin)

/admin/                         → Django admin panel
```

---

## 🧪 Edge Cases Handled

| Scenario | Handling |
|----------|----------|
| No stock | `issue_book()` returns error message |
| Duplicate issue | Checked before issuance, returns error |
| Max 3 books | Enforced in both model and form |
| Book deletion with active issues | Blocked with error message |
| Admin can't be issued books | Excluded from user dropdown |
| Fine on already-returned book | `process_return()` raises ValidationError |
| Fine waive/pay on non-pending | `mark_fine_paid/waive_fine()` raises ValidationError |
| Late fine calculation | Computed as `(return_date - due_date).days × rate` |

---

## 🔧 Customisation

**Change fine rate or loan period** — edit `library/settings.py`:
```python
FINE_RATE_PER_DAY = 10     # increase to ₹10/day
LOAN_PERIOD_DAYS = 14      # extend to 14-day loans
MAX_BOOKS_PER_USER = 5     # allow 5 books
```

**Add a new role** — add to `User.Role` choices in `accounts/models.py` and update permission mixins.

**Use PostgreSQL** — replace the `DATABASES` block in `settings.py` and install `psycopg2-binary`.
