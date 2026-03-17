from rest_framework import generics, permissions

from core.models import Seat

from .serializers import SeatMapSerializer


class SessionSeatMapView(generics.ListAPIView):
    serializer_class = SeatMapSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Seat.objects.filter(screening_id=self.kwargs["screening_id"]).order_by("row", "seat_number")
