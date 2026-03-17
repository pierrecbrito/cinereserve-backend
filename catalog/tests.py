from datetime import date, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Movie, Screen, Screening, Theater


class CatalogApiTests(APITestCase):
    def setUp(self):
        theater = Theater.objects.create(name="Cinepolis", city="Natal", address="Av X", phone="99999")
        screen = Screen.objects.create(theater=theater, screen_number=1, total_seats=100)

        self.movie = Movie.objects.create(
            title="Movie A",
            description="Desc",
            director="Dir",
            genre="Action",
            duration_minutes=120,
            release_date=date.today(),
            rating=4.5,
        )
        self.movie2 = Movie.objects.create(
            title="Movie B",
            description="Desc",
            director="Dir",
            genre="Drama",
            duration_minutes=90,
            release_date=date.today() - timedelta(days=1),
            rating=4.0,
        )
        Screening.objects.create(
            movie=self.movie,
            screen=screen,
            start_time=timezone.now() + timedelta(hours=2),
            price_per_seat=0,
            capacity=100,
        )

    def test_movies_list_is_paginated(self):
        response = self.client.get(reverse("movies-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_movie_sessions_list(self):
        response = self.client.get(reverse("movie-sessions-list", kwargs={"movie_id": self.movie.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
