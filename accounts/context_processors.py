"""
Context processors to make user-specific data available in all templates.
"""
from django.utils import timezone
from transactions.models import BookIssue


def user_notifications(request):
    """
    Add overdue books and pending fines to context for all pages.
    """
    context = {
        'my_overdue': [],
        'pending_fines': [],
        'total_pending_fine': 0,
    }
    
    if request.user.is_authenticated and not request.user.is_admin_user:
        now = timezone.now().date()
        
        # Get user's overdue books
        my_overdue = BookIssue.objects.filter(
            user=request.user,
            return_date__isnull=True,
            due_date__lt=now
        ).select_related('book')
        
        # Get pending fines
        pending_fines = BookIssue.objects.filter(
            user=request.user,
            fine_status=BookIssue.FineStatus.PENDING
        ).select_related('book')
        
        # Calculate total pending fine
        total_fine = sum(issue.fine_amount for issue in pending_fines)
        
        context.update({
            'my_overdue': my_overdue,
            'pending_fines': pending_fines,
            'total_pending_fine': total_fine,
        })
    
    return context
