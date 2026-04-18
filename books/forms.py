from django import forms
from .models import Book, Category


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = (
            'title', 'author', 'isbn', 'category', 'publisher',
            'publication_year', 'description', 'total_quantity',
            'available_quantity', 'shelf_location'
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'total_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'shelf_location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_quantity')
        available = cleaned_data.get('available_quantity')
        if total is not None and available is not None:
            if available > total:
                raise forms.ValidationError(
                    'Available quantity cannot exceed total quantity.'
                )
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BookSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, author, ISBN, or category...',
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    available_only = forms.BooleanField(
        required=False,
        label='Available only',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
