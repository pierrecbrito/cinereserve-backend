from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "user", "screening", "created_at")
    search_fields = ("code", "user__email", "user__username")
    list_filter = ("created_at",)
