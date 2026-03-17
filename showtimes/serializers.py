from django.core.cache import cache
from rest_framework import serializers

from core.models import Seat


class SeatMapSerializer(serializers.ModelSerializer):
    display_status = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["id", "row", "seat_number", "display_status"]

    def get_display_status(self, obj):
        # SOLD seats are treated as permanently purchased in the seat map.
        if obj.status == Seat.STATUS_SOLD:
            return "PURCHASED"

        if obj.status == Seat.STATUS_BLOCKED:
            return "RESERVED"

        lock_key = f"seat_lock:{obj.screening_id}:{obj.id}"
        if cache.get(lock_key) is not None:
            return "RESERVED"

        return "AVAILABLE"
