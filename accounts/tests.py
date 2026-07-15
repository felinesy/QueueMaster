from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from dashboard.forms import AppointmentForm
from dashboard.models import Appointment, BusinessHours, Service
from .forms import CustomerAppointmentForm
from .models import Customer


class CustomerAppointmentFormTests(TestCase):
    def test_booking_form_sets_today_and_business_hour_limits(self):
        BusinessHours.objects.create(open_time="09:00:00", close_time="17:00:00")

        form = CustomerAppointmentForm()
        today = timezone.localdate().strftime("%Y-%m-%d")

        self.assertEqual(form.fields["date"].widget.attrs["min"], today)
        self.assertEqual(form.fields["time"].widget.attrs["min"], "09:00")
        self.assertEqual(form.fields["time"].widget.attrs["max"], "17:00")

    def test_new_appointments_start_as_pending_until_approval(self):
        user = User.objects.create_user(username="customer", password="pass1234")
        customer = Customer.objects.create(user=user)
        service = Service.objects.create(service_name="Haircut", description="", price=10.00, duration=30)

        appointment = Appointment.objects.create(
            customer=customer,
            service=service,
            date=timezone.localdate(),
            time="10:00:00",
        )

        self.assertEqual(appointment.status, "Pending")

    def test_customer_cancellation_marks_appointment_as_cancelled(self):
        user = User.objects.create_user(username="customer2", password="pass1234")
        customer = Customer.objects.create(user=user)
        service = Service.objects.create(service_name="Massage", description="", price=20.00, duration=45)
        appointment = Appointment.objects.create(
            customer=customer,
            service=service,
            date=timezone.localdate(),
            time="11:00:00",
            status="Waiting",
        )

        self.client.force_login(user)
        response = self.client.get(reverse("customer_cancel_appointment", args=[appointment.pk]))

        appointment.refresh_from_db()
        self.assertEqual(appointment.status, "Cancelled")
        self.assertEqual(response.status_code, 302)

    def test_manual_queue_number_must_be_unique_for_the_same_day(self):
        user = User.objects.create_user(username="staff", password="pass1234")
        customer = Customer.objects.create(user=user)
        service = Service.objects.create(service_name="Nails", description="", price=15.00, duration=20)
        today = timezone.localdate()

        Appointment.objects.create(customer=customer, service=service, date=today, time="09:00:00", queue_number=1)
        appointment = Appointment.objects.create(customer=customer, service=service, date=today, time="10:00:00")

        form = AppointmentForm(
            data={
                "customer": customer.pk,
                "service": service.pk,
                "date": today,
                "time": "10:00:00",
                "status": "Waiting",
                "queue_number": 1,
            },
            instance=appointment,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("queue_number", form.errors)
