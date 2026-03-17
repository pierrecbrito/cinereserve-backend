from django.urls import path

from .views import CheckoutReservationView, ReserveSeatsView

urlpatterns = [
    path("sessions/<int:screening_id>/reserve/", ReserveSeatsView.as_view(), name="reserve-seats"),
    path("reservations/<int:reservation_id>/checkout/", CheckoutReservationView.as_view(), name="checkout-reservation"),
]
