from django.contrib import admin
from .models import Book, Category
from accounts.admin import admin_site


@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Book, site=admin_site)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'total_quantity', 'available_quantity')
    list_filter = ('category',)
    search_fields = ('title', 'author', 'isbn')
    readonly_fields = ('created_at', 'updated_at')
