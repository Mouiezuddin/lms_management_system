from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    Roles: Admin, Student, Faculty
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STUDENT = 'STUDENT', 'Student'
        FACULTY = 'FACULTY', 'Faculty'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_faculty(self):
        return self.role == self.Role.FACULTY

    @property
    def can_manage_books(self):
        """Admin can manage books."""
        return self.role == self.Role.ADMIN

    @property
    def active_issues_count(self):
        """Count of currently issued books."""
        return self.bookissue_set.filter(return_date__isnull=True).count()

    def has_module_perms(self, app_label):
        """Only admin users can access admin panel."""
        if self.is_superuser:
            return True
        return self.role == self.Role.ADMIN and self.is_staff

    def has_perm(self, perm, obj=None):
        """Only admin users have permissions."""
        if self.is_superuser:
            return True
        return self.role == self.Role.ADMIN and self.is_staff
