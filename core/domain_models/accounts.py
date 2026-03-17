from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended User model for CineReserve."""

    phone = models.CharField(max_length=15, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email
