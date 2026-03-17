from rest_framework import serializers

from core.models import Reservation


class ReserveSeatsSerializer(serializers.Serializer):
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )


class ReservationSerializer(serializers.ModelSerializer):
    seat_ids = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ["id", "status", "screening_id", "seat_ids", "total_price", "expires_at", "created_at"]

    def get_seat_ids(self, obj):
        return list(obj.seats.values_list("id", flat=True))
