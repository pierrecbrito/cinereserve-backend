from datetime import date, timedelta

from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Movie, Screen, Screening, Seat, Theater


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class SeatMapApiTests(APITestCase):
    def setUp(self):
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
        self.screening = Screening.objects.create(
            movie=movie,
            screen=screen,
            start_time=timezone.now() + timedelta(hours=2),
            price_per_seat=0,
            capacity=100,
        )
        Seat.objects.create(screening=self.screening, seat_number=1, row="A", status=Seat.STATUS_AVAILABLE)
        Seat.objects.create(screening=self.screening, seat_number=2, row="A", status=Seat.STATUS_SOLD)

    def test_seat_map_returns_display_status(self):
        response = self.client.get(reverse("session-seat-map", kwargs={"screening_id": self.screening.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["display_status"], "AVAILABLE")
        self.assertEqual(response.data["results"][1]["display_status"], "PURCHASED")
