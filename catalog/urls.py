from django.urls import path

from .views import MovieListView, MovieSessionsListView

urlpatterns = [
    path("movies/", MovieListView.as_view(), name="movies-list"),
    path("movies/<int:movie_id>/sessions/", MovieSessionsListView.as_view(), name="movie-sessions-list"),
]
