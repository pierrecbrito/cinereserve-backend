from django.utils import timezone
from rest_framework import serializers

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="screening.movie.title", read_only=True)
    session_start = serializers.DateTimeField(source="screening.start_time", read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ["id", "code", "movie_title", "session_start", "created_at", "is_active"]

    def get_is_active(self, obj):
        return obj.screening.start_time >= timezone.now()
