from datetime import date, timedelta

from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Movie, Reservation, Screen, Screening, Theater, User
from tickets.models import Ticket


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class MyTicketsApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user2", email="user2@example.com", password="StrongPass123")
        self.client.force_authenticate(self.user)

        theater = Theater.objects.create(name="Cinepolis", city="Natal", address="Av X", phone="99999")
        screen = Screen.objects.create(theater=theater, screen_number=1, total_seats=100)
        movie = Movie.objects.create(
            title="Movie A",
            description="Desc",
            director="Dir",
            genre="Action",
            duration_minutes=120,
            release_date=date.today(),
            rating=4.5,
        )
        screening = Screening.objects.create(
            movie=movie,
            screen=screen,
            start_time=timezone.now() + timedelta(hours=2),
            price_per_seat=0,
            capacity=100,
        )
        reservation = Reservation.objects.create(
            user=self.user,
            screening=screening,
            status=Reservation.STATUS_CONFIRMED,
            total_price=0,
            expires_at=timezone.now(),
        )
        Ticket.objects.create(user=self.user, reservation=reservation, screening=screening)

    def test_my_tickets_list_returns_paginated_results(self):
        response = self.client.get(reverse("my-tickets"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
