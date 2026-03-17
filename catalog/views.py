from rest_framework import generics, permissions

from core.models import Movie, Screening

from .serializers import MovieListSerializer, MovieSessionSerializer


class MovieListView(generics.ListAPIView):
    serializer_class = MovieListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Movie.objects.all().order_by("-release_date")
    search_fields = ["title", "director", "genre"]
    ordering_fields = ["release_date", "rating", "title"]


class MovieSessionsListView(generics.ListAPIView):
    serializer_class = MovieSessionSerializer
    permission_classes = [permissions.AllowAny]
    ordering_fields = ["start_time"]

    def get_queryset(self):
        movie_id = self.kwargs["movie_id"]
        return (
            Screening.objects.select_related("movie", "screen", "screen__theater")
            .filter(movie_id=movie_id)
            .order_by("start_time")
        )
