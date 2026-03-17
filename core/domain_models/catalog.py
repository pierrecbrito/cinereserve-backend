from django.core.validators import MinValueValidator
from django.db import models


class Movie(models.Model):
    """Movie catalog."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    director = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    release_date = models.DateField()
    poster_url = models.URLField(blank=True)
    rating = models.FloatField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "movies"
        ordering = ["-release_date"]

    def __str__(self):
        return self.title
