from django.urls import path

from .views import SessionSeatMapView

urlpatterns = [
    path("sessions/<int:screening_id>/seats/", SessionSeatMapView.as_view(), name="session-seat-map"),
]
