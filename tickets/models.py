import uuid

from django.conf import settings
from django.db import models


class Ticket(models.Model):
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.OneToOneField("core.Reservation", on_delete=models.CASCADE, related_name="ticket")
    screening = models.ForeignKey("core.Screening", on_delete=models.CASCADE, related_name="tickets")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tickets"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ticket {self.code}"
