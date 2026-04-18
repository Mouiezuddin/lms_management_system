from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.views.generic import View, TemplateView, CreateView, UpdateView, ListView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import LoginForm, UserRegistrationForm, UserUpdateForm
from .models import User
from books.models import Book
from transactions.models import BookIssue


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin that restricts access to admin users only."""

    def test_func(self):
        return self.request.user.is_admin_user


class LoginView(View):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = self.form_class(request)
        return self._render(request, form)

    def post(self, request):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        return self._render(request, form)

    def _render(self, request, form):
        from django.shortcuts import render
        return render(request, self.template_name, {'form': form})


class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('accounts:login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now().date()

        total_books = Book.objects.aggregate(
            total=__import__('django.db.models', fromlist=['Sum']).Sum('total_quantity')
        )['total'] or 0
        available_books = Book.objects.aggregate(
            total=__import__('django.db.models', fromlist=['Sum']).Sum('available_quantity')
        )['total'] or 0

        issued_qs = BookIssue.objects.filter(return_date__isnull=True)
        overdue_qs = issued_qs.filter(due_date__lt=now)

        ctx.update({
            'total_books': total_books,
            'available_books': available_books,
            'issued_count': issued_qs.count(),
            'overdue_count': overdue_qs.count(),
            'total_titles': Book.objects.count(),
        })

        if self.request.user.is_admin_user:
            ctx['recent_issues'] = BookIssue.objects.select_related(
                'user', 'book'
            ).order_by('-issue_date')[:10]
            ctx['overdue_issues'] = overdue_qs.select_related('user', 'book')[:5]
            ctx['total_users'] = User.objects.count()
        else:
            user_issues = BookIssue.objects.filter(
                user=self.request.user
            ).select_related('book').order_by('-issue_date')
            ctx['my_issues'] = user_issues.filter(return_date__isnull=True)
            ctx['my_history'] = user_issues.filter(return_date__isnull=False)[:5]
            ctx['my_overdue'] = user_issues.filter(
                return_date__isnull=True, due_date__lt=now
            )
            ctx['pending_fines'] = user_issues.filter(
                fine_status=BookIssue.FineStatus.PENDING
            )
            
            # Calculate total pending fine amount
            total_fine = sum(issue.fine_amount for issue in ctx['pending_fines'])
            ctx['total_pending_fine'] = total_fine

        return ctx


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.all().order_by('username')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q)
            )
        return qs


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Create User'
        return ctx


class RegisterView(CreateView):
    """Public registration view for new users."""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Account created successfully! Please log in with your credentials.'
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Create Account'
        return ctx


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit User'
        return ctx


class ProfileView(LoginRequiredMixin, UpdateView):
    """View for users to edit their own profile."""
    model = User
    template_name = 'accounts/profile.html'
    fields = ['first_name', 'last_name', 'email', 'phone', 'address']
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'My Profile'
        return ctx
