from django.core.validators import MinValueValidator
from django.db import models


class Theater(models.Model):
    """Cinema/Theater location."""

    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "theaters"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.city}"


class Screen(models.Model):
    """Screen/Room within a theater."""

    theater = models.ForeignKey("core.Theater", on_delete=models.CASCADE, related_name="screens")
    screen_number = models.IntegerField()
    total_seats = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "screens"
        unique_together = ["theater", "screen_number"]
        ordering = ["theater", "screen_number"]

    def __str__(self):
        return f"{self.theater.name} - Sala {self.screen_number}"

    def available_seats_count(self):
        """Count seats currently reserved for screenings in this room."""

        return (
            self.screenings.filter(seats__status="RESERVED")
            .values("seats__id")
            .distinct()
            .count()
        )
