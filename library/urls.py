from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from accounts.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('books/', include('books.urls', namespace='books')),
    path('transactions/', include('transactions.urls', namespace='transactions')),
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=True)),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]
