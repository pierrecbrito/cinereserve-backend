from datetime import timedelta

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.models import Reservation, Seat, Screening
from tickets.models import Ticket


LOCK_TTL_SECONDS = 10 * 60


def seat_lock_key(screening_id: int, seat_id: int) -> str:
    return f"seat_lock:{screening_id}:{seat_id}"


def reserve_seats(*, user, screening_id: int, seat_ids: list[int]) -> Reservation:
    screening = Screening.objects.filter(id=screening_id).first()
    if not screening:
        raise ValidationError("Screening not found.")

    seats = list(Seat.objects.filter(id__in=seat_ids, screening_id=screening_id))
    if len(seats) != len(set(seat_ids)):
        raise ValidationError("One or more seats are invalid for this screening.")

    for seat in seats:
        if seat.status == Seat.STATUS_SOLD:
            raise ValidationError(f"Seat {seat.id} is already purchased.")

    acquired_keys = []
    user_locks = []
    try:
        for seat in seats:
            key = seat_lock_key(screening_id, seat.id)
            owner = cache.get(key)
            if owner == user.id:
                user_locks.append(key)
                continue
            if cache.add(key, user.id, timeout=LOCK_TTL_SECONDS):
                acquired_keys.append(key)
                continue
            raise ValidationError(f"Seat {seat.id} is already reserved.")

        with transaction.atomic():
            reservation = Reservation.objects.create(
                user=user,
                screening=screening,
                status=Reservation.STATUS_PENDING,
                total_price=0,
                expires_at=timezone.now() + timedelta(seconds=LOCK_TTL_SECONDS),
            )
            reservation.seats.set(seats)
        return reservation
    except Exception:
        for key in acquired_keys:
            cache.delete(key)
        raise


def checkout_reservation(*, user, reservation_id: int) -> Ticket:
    with transaction.atomic():
        reservation = (
            Reservation.objects.select_for_update()
            .select_related("screening", "user")
            .filter(id=reservation_id, user_id=user.id)
            .first()
        )

        if not reservation:
            raise ValidationError("Reservation not found.")

        if reservation.status != Reservation.STATUS_PENDING:
            raise ValidationError("Reservation is not pending.")

        if reservation.is_expired():
            reservation.status = Reservation.STATUS_EXPIRED
            reservation.save(update_fields=["status", "updated_at"])
            raise ValidationError("Reservation expired.")

        seats = list(reservation.seats.select_for_update())
        for seat in seats:
            key = seat_lock_key(reservation.screening_id, seat.id)
            owner = cache.get(key)
            if owner != user.id:
                raise ValidationError(f"Seat {seat.id} lock is missing or owned by another user.")
            if seat.status == Seat.STATUS_SOLD:
                raise ValidationError(f"Seat {seat.id} has already been purchased.")

        Seat.objects.filter(id__in=[seat.id for seat in seats]).update(status=Seat.STATUS_SOLD)
        reservation.status = Reservation.STATUS_CONFIRMED
        reservation.expires_at = timezone.now()
        reservation.save(update_fields=["status", "expires_at", "updated_at"])

        ticket, _ = Ticket.objects.get_or_create(
            reservation=reservation,
            defaults={
                "user": reservation.user,
                "screening": reservation.screening,
            },
        )

        for seat in seats:
            cache.delete(seat_lock_key(reservation.screening_id, seat.id))

        return ticket
