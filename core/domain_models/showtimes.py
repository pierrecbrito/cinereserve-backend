from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Screening(models.Model):
    """Movie session/showing."""

    movie = models.ForeignKey("core.Movie", on_delete=models.CASCADE, related_name="screenings")
    screen = models.ForeignKey("core.Screen", on_delete=models.CASCADE, related_name="screenings")
    start_time = models.DateTimeField()
    price_per_seat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "screenings"
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.movie.title} - {self.start_time}"

    def available_seats(self):
        """Get count of available seats."""

        return self.seats.filter(status="AVAILABLE").count()

    def is_past(self):
        """Check if screening is in the past."""

        return self.start_time < timezone.now()


class Seat(models.Model):
    """Individual seat in a screening."""

    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_RESERVED = "RESERVED"
    STATUS_SOLD = "SOLD"
    STATUS_BLOCKED = "BLOCKED"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_SOLD, "Sold"),
        (STATUS_BLOCKED, "Blocked"),
    ]

    screening = models.ForeignKey("core.Screening", on_delete=models.CASCADE, related_name="seats")
    seat_number = models.IntegerField()
    row = models.CharField(max_length=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "seats"
        unique_together = ["screening", "row", "seat_number"]
        ordering = ["row", "seat_number"]

    def __str__(self):
        return f"{self.screening} - {self.row}{self.seat_number}"
