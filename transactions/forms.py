from django import forms
from django.conf import settings
from .models import BookIssue
from books.models import Book
from accounts.models import User


class IssueBookForm(forms.Form):
    """Form for admin to issue a book to a user."""
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).exclude(role=User.Role.ADMIN),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Issue To',
        empty_label='Select a user...',
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(available_quantity__gt=0).select_related('category'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Book',
        empty_label='Select a book...',
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Notes (optional)',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize book field to show category in display
        self.fields['book'].queryset = Book.objects.filter(
            available_quantity__gt=0
        ).select_related('category').order_by('category__name', 'title')

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        book = cleaned_data.get('book')

        if user and book:
            max_books = getattr(settings, 'MAX_BOOKS_PER_USER', 3)
            active_count = BookIssue.objects.filter(
                user=user, return_date__isnull=True
            ).count()
            if active_count >= max_books:
                raise forms.ValidationError(
                    f'{user.get_full_name() or user.username} already has {active_count} '
                    f'book(s) issued (max: {max_books}).'
                )
            already_issued = BookIssue.objects.filter(
                user=user, book=book, return_date__isnull=True
            ).exists()
            if already_issued:
                raise forms.ValidationError(
                    f'{user.get_full_name() or user.username} already has '
                    f'"{book.title}" issued.'
                )
        return cleaned_data


class SelfIssueForm(forms.Form):
    """Form for students/faculty to request a book (admin still confirms)."""
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(available_quantity__gt=0),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select a book...',
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    )


class ReturnBookForm(forms.Form):
    """Confirmation form for returning a book."""
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Return Notes (optional)',
    )


class FinePaymentForm(forms.Form):
    """Admin form to record fine payment."""
    action = forms.ChoiceField(
        choices=[('pay', 'Mark as Paid'), ('waive', 'Waive Fine')],
        widget=forms.RadioSelect(),
        initial='pay',
    )
