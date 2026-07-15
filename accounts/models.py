from django.conf import settings
from django.db import models

class Role(models.Model):
    role_name = models.CharField(max_length=50)

    def __str__(self):
        return self.role_name


class User(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Notification(models.Model):
    """Simple notification model for in-app realtime notifications."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    level = models.CharField(max_length=20, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}: {self.message[:50]}"