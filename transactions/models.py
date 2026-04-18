from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime


class BookIssue(models.Model):
    """
    Represents a book loan transaction.
    Handles issuance, return, and fine calculation.
    """

    class FineStatus(models.TextChoices):
        NOT_APPLICABLE = 'NA', 'Not Applicable'
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        WAIVED = 'WAIVED', 'Waived'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookissue_set'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='bookissue_set'
    )
    issue_date = models.DateField(default=datetime.date.today)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    # Fine fields
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fine_status = models.CharField(
        max_length=10,
        choices=FineStatus.choices,
        default=FineStatus.NOT_APPLICABLE
    )
    fine_paid_at = models.DateTimeField(null=True, blank=True)

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='issued_transactions'
    )
    returned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='received_transactions'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'return_date']),
            models.Index(fields=['book', 'return_date']),
            models.Index(fields=['due_date']),
        ]
        verbose_name = 'Book Issue'
        verbose_name_plural = 'Book Issues'

    def __str__(self):
        status = 'Returned' if self.return_date else 'Active'
        return f"{self.book.title} → {self.user.username} [{status}]"

    @property
    def is_active(self):
        return self.return_date is None

    @property
    def is_overdue(self):
        if self.return_date:
            return self.return_date > self.due_date
        return datetime.date.today() > self.due_date

    @property
    def late_days(self):
        if not self.is_overdue:
            return 0
        end_date = self.return_date or datetime.date.today()
        delta = end_date - self.due_date
        return max(0, delta.days)

    @property
    def calculated_fine(self):
        """Calculate fine based on late days × rate."""
        rate = getattr(settings, 'FINE_RATE_PER_DAY', 5)
        return self.late_days * rate

    def save(self, *args, **kwargs):
        # Auto-set due_date on first save
        if not self.pk and not self.due_date:
            loan_days = getattr(settings, 'LOAN_PERIOD_DAYS', 7)
            self.due_date = self.issue_date + datetime.timedelta(days=loan_days)
        super().save(*args, **kwargs)

    # ── Business Logic ──────────────────────────────────────────────────────

    @classmethod
    def issue_book(cls, user, book, issued_by=None):
        """
        Issue a book to a user. Enforces all business rules.
        Returns (BookIssue instance, None) on success,
        or (None, error_message) on failure.
        """
        max_books = getattr(settings, 'MAX_BOOKS_PER_USER', 3)
        loan_days = getattr(settings, 'LOAN_PERIOD_DAYS', 7)

        # Rule 1: Book availability
        if not book.is_available:
            return None, f'"{book.title}" is currently out of stock.'

        # Rule 2: Max books per user
        active_count = cls.objects.filter(user=user, return_date__isnull=True).count()
        if active_count >= max_books:
            return None, (
                f'User already has {active_count} book(s) issued. '
                f'Maximum allowed is {max_books}.'
            )

        # Rule 3: Duplicate issue check
        already_issued = cls.objects.filter(
            user=user, book=book, return_date__isnull=True
        ).exists()
        if already_issued:
            return None, f'User already has "{book.title}" issued.'

        today = datetime.date.today()
        issue = cls(
            user=user,
            book=book,
            issue_date=today,
            due_date=today + datetime.timedelta(days=loan_days),
            issued_by=issued_by,
        )
        issue.save()

        # Decrement available quantity
        book.available_quantity -= 1
        book.save(update_fields=['available_quantity'])

        return issue, None

    def process_return(self, returned_to=None):
        """
        Process a book return. Calculates fine if overdue.
        Returns fine_amount (0 if no fine).
        """
        if self.return_date is not None:
            raise ValidationError('This book has already been returned.')

        today = datetime.date.today()
        self.return_date = today
        self.returned_to = returned_to

        # Calculate fine
        fine = self.calculated_fine
        if fine > 0:
            self.fine_amount = fine
            self.fine_status = self.FineStatus.PENDING
        else:
            self.fine_amount = 0
            self.fine_status = self.FineStatus.NOT_APPLICABLE

        self.save()

        # Increment available quantity
        self.book.available_quantity += 1
        self.book.save(update_fields=['available_quantity'])

        return fine

    def mark_fine_paid(self):
        """Mark the fine as paid."""
        if self.fine_status != self.FineStatus.PENDING:
            raise ValidationError('Fine is not in PENDING state.')
        self.fine_status = self.FineStatus.PAID
        self.fine_paid_at = timezone.now()
        self.save(update_fields=['fine_status', 'fine_paid_at'])

    def waive_fine(self):
        """Admin can waive a pending fine."""
        if self.fine_status != self.FineStatus.PENDING:
            raise ValidationError('Fine is not in PENDING state.')
        self.fine_status = self.FineStatus.WAIVED
        self.save(update_fields=['fine_status'])
