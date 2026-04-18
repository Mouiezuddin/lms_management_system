from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from accounts.views import AdminRequiredMixin
from .models import Book, Category
from .forms import BookForm, CategoryForm, BookSearchForm


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        qs = Book.objects.select_related('category').order_by('title')
        form = BookSearchForm(self.request.GET)

        if form.is_valid():
            q = form.cleaned_data.get('q')
            category = form.cleaned_data.get('category')
            available_only = form.cleaned_data.get('available_only')

            if q:
                qs = Book.search(q)
            if category:
                qs = qs.filter(category=category)
            if available_only:
                qs = qs.filter(available_quantity__gt=0)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = BookSearchForm(self.request.GET)
        ctx['total_results'] = self.get_queryset().count()
        return ctx


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        book = self.get_object()
        user = self.request.user
        # Check if current user has this book issued
        ctx['user_has_issued'] = book.bookissue_set.filter(
            user=user, return_date__isnull=True
        ).exists()
        ctx['recent_issues'] = book.bookissue_set.select_related(
            'user'
        ).order_by('-issue_date')[:5] if user.is_admin_user else None
        return ctx


class BookCreateView(AdminRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')

    def form_valid(self, form):
        messages.success(self.request, f'Book "{form.instance.title}" added successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add New Book'
        ctx['button_label'] = 'Add Book'
        return ctx


class BookUpdateView(AdminRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')

    def form_valid(self, form):
        messages.success(self.request, f'Book "{form.instance.title}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Book'
        ctx['button_label'] = 'Save Changes'
        return ctx


class BookDeleteView(AdminRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')
    context_object_name = 'book'

    def form_valid(self, form):
        book = self.get_object()
        # Prevent deletion if there are active issues
        if book.bookissue_set.filter(return_date__isnull=True).exists():
            messages.error(
                self.request,
                'Cannot delete this book — there are active issues. '
                'Please ensure all copies are returned first.'
            )
            from django.shortcuts import redirect
            return redirect('books:book_detail', pk=book.pk)
        messages.success(self.request, f'Book "{book.title}" deleted successfully.')
        return super().form_valid(form)


class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'books/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'books/category_form.html'
    success_url = reverse_lazy('books:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully.')
        return super().form_valid(form)


class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'books/category_form.html'
    success_url = reverse_lazy('books:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully.')
        return super().form_valid(form)
