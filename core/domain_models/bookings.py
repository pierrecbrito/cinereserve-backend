from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Reservation(models.Model):
    """Ticket reservation."""

    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_EXPIRED = "EXPIRED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_EXPIRED, "Expired"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")
    screening = models.ForeignKey("core.Screening", on_delete=models.CASCADE, related_name="reservations")
    seats = models.ManyToManyField("core.Seat", related_name="reservations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reservations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reservation #{self.id} - {self.user.email}"

    def is_expired(self):
        """Check if reservation is expired."""

        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        """Auto-set expiration time to 10 minutes from creation."""

        if not self.pk:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
