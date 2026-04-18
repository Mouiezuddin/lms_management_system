from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, View, FormView, TemplateView

import datetime

from accounts.views import AdminRequiredMixin
from accounts.models import User
from books.models import Book
from .models import BookIssue
from .forms import IssueBookForm, ReturnBookForm, FinePaymentForm


class TransactionListView(AdminRequiredMixin, ListView):
    model = BookIssue
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        qs = BookIssue.objects.select_related('user', 'book', 'issued_by').order_by('-issue_date')

        # Filters
        status = self.request.GET.get('status')
        if status == 'active':
            qs = qs.filter(return_date__isnull=True)
        elif status == 'returned':
            qs = qs.filter(return_date__isnull=False)
        elif status == 'overdue':
            qs = qs.filter(return_date__isnull=True, due_date__lt=datetime.date.today())

        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(user__username__icontains=q) |
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(book__title__icontains=q) |
                Q(book__isbn__icontains=q)
            )

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_filter'] = self.request.GET.get('status', '')
        ctx['q'] = self.request.GET.get('q', '')
        today = datetime.date.today()
        ctx['overdue_count'] = BookIssue.objects.filter(
            return_date__isnull=True, due_date__lt=today
        ).count()
        return ctx


class MyTransactionsView(LoginRequiredMixin, ListView):
    model = BookIssue
    template_name = 'transactions/my_transactions.html'
    context_object_name = 'transactions'
    paginate_by = 15

    def get_queryset(self):
        return BookIssue.objects.filter(
            user=self.request.user
        ).select_related('book').order_by('-issue_date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = datetime.date.today()
        qs = self.get_queryset()
        ctx['active_issues'] = qs.filter(return_date__isnull=True)
        ctx['history'] = qs.filter(return_date__isnull=False)
        ctx['pending_fines'] = qs.filter(fine_status=BookIssue.FineStatus.PENDING)
        return ctx


class IssueBookView(AdminRequiredMixin, FormView):
    template_name = 'transactions/issue_book.html'
    form_class = IssueBookForm
    success_url = reverse_lazy('transactions:transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pre-select book if passed via GET
        if self.request.method == 'GET' and 'book' in self.request.GET:
            kwargs['initial'] = {'book': self.request.GET.get('book')}
        return kwargs

    def form_valid(self, form):
        user = form.cleaned_data['user']
        book = form.cleaned_data['book']
        notes = form.cleaned_data.get('notes', '')

        issue, error = BookIssue.issue_book(
            user=user,
            book=book,
            issued_by=self.request.user
        )

        if error:
            messages.error(self.request, error)
            return self.form_invalid(form)

        if notes:
            issue.notes = notes
            issue.save(update_fields=['notes'])

        messages.success(
            self.request,
            f'✓ "{book.title}" issued to {user.get_full_name() or user.username}. '
            f'Due date: {issue.due_date.strftime("%d %b %Y")}.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Issue Book'
        from books.models import Category
        ctx['categories'] = Category.objects.all().order_by('name')
        return ctx


class ReturnBookView(AdminRequiredMixin, View):
    template_name = 'transactions/return_book.html'

    def get(self, request, pk):
        issue = get_object_or_404(BookIssue, pk=pk, return_date__isnull=True)
        form = ReturnBookForm()
        return self._render(request, issue, form)

    def post(self, request, pk):
        issue = get_object_or_404(BookIssue, pk=pk, return_date__isnull=True)
        form = ReturnBookForm(request.POST)

        if form.is_valid():
            try:
                fine = issue.process_return(returned_to=request.user)
                if form.cleaned_data.get('notes'):
                    issue.notes += f'\n[Return] {form.cleaned_data["notes"]}'
                    issue.save(update_fields=['notes'])

                if fine > 0:
                    messages.warning(
                        request,
                        f'Book returned with a fine of ₹{fine:.2f} '
                        f'({issue.late_days} day(s) overdue). Fine is pending payment.'
                    )
                else:
                    messages.success(request, f'✓ "{issue.book.title}" returned successfully. No fine.')
            except ValidationError as e:
                messages.error(request, str(e))

            return redirect('transactions:transaction_list')

        return self._render(request, issue, form)

    def _render(self, request, issue, form):
        from django.shortcuts import render
        ctx = {
            'issue': issue,
            'form': form,
            'projected_fine': issue.calculated_fine,
            'late_days': issue.late_days,
        }
        return render(request, self.template_name, ctx)


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = BookIssue
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'issue'

    def get_queryset(self):
        qs = BookIssue.objects.select_related('user', 'book', 'issued_by', 'returned_to')
        # Non-admins can only see their own
        if not self.request.user.is_admin_user:
            qs = qs.filter(user=self.request.user)
        return qs


class FineManagementView(AdminRequiredMixin, View):
    template_name = 'transactions/fine_management.html'

    def get(self, request, pk):
        issue = get_object_or_404(
            BookIssue.objects.select_related('user', 'book'),
            pk=pk,
            fine_status=BookIssue.FineStatus.PENDING
        )
        form = FinePaymentForm()
        from django.shortcuts import render
        return render(request, self.template_name, {'issue': issue, 'form': form})

    def post(self, request, pk):
        issue = get_object_or_404(
            BookIssue,
            pk=pk,
            fine_status=BookIssue.FineStatus.PENDING
        )
        form = FinePaymentForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data['action']
            try:
                if action == 'pay':
                    issue.mark_fine_paid()
                    messages.success(request, f'Fine of ₹{issue.fine_amount} marked as paid.')
                elif action == 'waive':
                    issue.waive_fine()
                    messages.success(request, f'Fine of ₹{issue.fine_amount} has been waived.')
            except ValidationError as e:
                messages.error(request, str(e))

        return redirect('transactions:transaction_detail', pk=pk)


class FineListView(AdminRequiredMixin, ListView):
    model = BookIssue
    template_name = 'transactions/fine_list.html'
    context_object_name = 'fines'
    paginate_by = 20

    def get_queryset(self):
        return BookIssue.objects.filter(
            fine_status=BookIssue.FineStatus.PENDING
        ).select_related('user', 'book').order_by('-return_date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_pending'] = BookIssue.objects.filter(
            fine_status=BookIssue.FineStatus.PENDING
        ).aggregate(total=Sum('fine_amount'))['total'] or 0
        return ctx
