from datetime import date, timedelta

from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Movie, Screen, Screening, Seat, Theater, User
from tickets.models import Ticket


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class BookingFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", email="user1@example.com", password="StrongPass123")
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
        self.screening = Screening.objects.create(
            movie=movie,
            screen=screen,
            start_time=timezone.now() + timedelta(hours=2),
            price_per_seat=0,
            capacity=100,
        )
        self.seat1 = Seat.objects.create(screening=self.screening, seat_number=1, row="A", status=Seat.STATUS_AVAILABLE)

    def test_reserve_and_checkout_generates_ticket(self):
        reserve_response = self.client.post(
            reverse("reserve-seats", kwargs={"screening_id": self.screening.id}),
            {"seat_ids": [self.seat1.id]},
            format="json",
        )
        self.assertEqual(reserve_response.status_code, status.HTTP_201_CREATED)

        reservation_id = reserve_response.data["id"]
        checkout_response = self.client.post(
            reverse("checkout-reservation", kwargs={"reservation_id": reservation_id}),
            {},
            format="json",
        )
        self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)
        self.seat1.refresh_from_db()
        self.assertEqual(self.seat1.status, Seat.STATUS_SOLD)
        self.assertTrue(Ticket.objects.filter(reservation_id=reservation_id).exists())
