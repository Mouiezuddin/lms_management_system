from django.contrib import admin
from .models import BookIssue
from accounts.admin import admin_site


@admin.register(BookIssue, site=admin_site)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = (
        'book', 'user', 'issue_date', 'due_date',
        'return_date', 'fine_amount', 'fine_status'
    )
    list_filter = ('fine_status', 'issue_date')
    search_fields = ('book__title', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'fine_paid_at')
    date_hierarchy = 'issue_date'
