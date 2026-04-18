from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Q


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    author = models.CharField(max_length=255, db_index=True)
    isbn = models.CharField(max_length=20, unique=True, verbose_name='ISBN')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='books'
    )
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    total_quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    available_quantity = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title', 'author']),
            models.Index(fields=['isbn']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def is_available(self):
        return self.available_quantity > 0

    @property
    def issued_count(self):
        return self.total_quantity - self.available_quantity

    def save(self, *args, **kwargs):
        # Ensure available_quantity doesn't exceed total_quantity
        if self.available_quantity > self.total_quantity:
            self.available_quantity = self.total_quantity
        super().save(*args, **kwargs)

    @classmethod
    def search(cls, query):
        """Full-text search across title, author, category."""
        if not query:
            return cls.objects.all()
        return cls.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(category__name__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()
