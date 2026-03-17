from rest_framework import serializers

from core.models import Movie, Screening


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "director",
            "genre",
            "duration_minutes",
            "release_date",
            "poster_url",
            "rating",
        ]


class MovieSessionSerializer(serializers.ModelSerializer):
    movie_id = serializers.IntegerField(source="movie.id", read_only=True)
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    theater_name = serializers.CharField(source="screen.theater.name", read_only=True)
    theater_city = serializers.CharField(source="screen.theater.city", read_only=True)
    screen_number = serializers.IntegerField(source="screen.screen_number", read_only=True)

    class Meta:
        model = Screening
        fields = [
            "id",
            "movie_id",
            "movie_title",
            "start_time",
            "price_per_seat",
            "capacity",
            "theater_name",
            "theater_city",
            "screen_number",
        ]
