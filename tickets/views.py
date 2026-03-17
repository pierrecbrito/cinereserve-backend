from rest_framework import generics, permissions

from .models import Ticket
from .serializers import TicketSerializer


class MyTicketsView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ["created_at", "screening__start_time"]

    def get_queryset(self):
        return (
            Ticket.objects.select_related("screening", "screening__movie")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )
