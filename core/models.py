from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.utils import timezone

class User(AbstractUser):
    """Extended User model for CineReserve"""
    phone = models.CharField(max_length=15, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email


class Movie(models.Model):
    """Movie catalog"""
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
        db_table = 'movies'
        ordering = ['-release_date']
    
    def __str__(self):
        return self.title


class Theater(models.Model):
    """Cinema/Theater location"""
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'theaters'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Screen(models.Model):
    """Screen/Room within a theater"""
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='screens')
    screen_number = models.IntegerField()
    total_seats = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'screens'
        unique_together = ['theater', 'screen_number']
        ordering = ['theater', 'screen_number']
    
    def __str__(self):
        return f"{self.theater.name} - Sala {self.screen_number}"
    
    def available_seats_count(self):
        """Count available seats"""
        reserved_seats = Seat.objects.filter(
            screen=self,
            status='RESERVED'
        ).count()
        return self.total_seats - reserved_seats


class Screening(models.Model):
    """Movie session/showing"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='screenings')
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='screenings')
    start_time = models.DateTimeField()
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'screenings'
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.movie.title} - {self.start_time}"
    
    def available_seats(self):
        """Get count of available seats"""
        return Seat.objects.filter(screening=self, status='AVAILABLE').count()
    
    def is_past(self):
        """Check if screening is in the past"""
        return self.start_time < timezone.now()


class Seat(models.Model):
    """Individual seat in a screening"""
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('RESERVED', 'Reserved'),
        ('SOLD', 'Sold'),
        ('BLOCKED', 'Blocked'),
    ]
    
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.IntegerField()
    row = models.CharField(max_length=2)  # A, B, C, etc
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'seats'
        unique_together = ['screening', 'row', 'seat_number']
        ordering = ['row', 'seat_number']
    
    def __str__(self):
        return f"{self.screening} - {self.row}{self.seat_number}"


class Reservation(models.Model):
    """Ticket reservation"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name='reservations')
    seats = models.ManyToManyField(Seat, related_name='reservations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Reservation expires after 10 minutes
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reservations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reservation #{self.id} - {self.user.email}"
    
    def is_expired(self):
        """Check if reservation is expired"""
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        """Auto-set expiration time to 10 minutes from creation"""
        if not self.pk:  # Only on creation
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment record"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=50)  # CREDIT_CARD, DEBIT_CARD, PIX
    transaction_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.get_status_display()}"