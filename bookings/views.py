from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.serializers import TicketSerializer

from .serializers import ReservationSerializer, ReserveSeatsSerializer
from .services import checkout_reservation, reserve_seats


class ReserveSeatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, screening_id):
        serializer = ReserveSeatsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = reserve_seats(
            user=request.user,
            screening_id=screening_id,
            seat_ids=serializer.validated_data["seat_ids"],
        )
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)


class CheckoutReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, reservation_id):
        ticket = checkout_reservation(user=request.user, reservation_id=reservation_id)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)
