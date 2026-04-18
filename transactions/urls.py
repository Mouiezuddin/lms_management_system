from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('mine/', views.MyTransactionsView.as_view(), name='my_transactions'),
    path('issue/', views.IssueBookView.as_view(), name='issue_book'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('<int:pk>/return/', views.ReturnBookView.as_view(), name='return_book'),
    path('<int:pk>/fine/', views.FineManagementView.as_view(), name='fine_management'),
    path('fines/', views.FineListView.as_view(), name='fine_list'),
]
