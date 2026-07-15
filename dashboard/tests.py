from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Customer, Staff
from .models import Appointment, Service


class AdminViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            password="secret123",
            is_staff=True,
            is_superuser=True,
        )
        self.customer_user = User.objects.create_user(username="customer", password="secret123")
        self.staff_user = User.objects.create_user(username="staff", password="secret123")

        self.customer = Customer.objects.create(user=self.customer_user, address="123 Main St")
        self.staff = Staff.objects.create(user=self.staff_user, position="Stylist")
        self.service = Service.objects.create(
            service_name="Haircut",
            description="Trim and style",
            price=25.00,
            duration=30,
        )
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            staff=self.staff,
            service=self.service,
            date="2026-07-11",
            time="10:00:00",
            status="Waiting",
        )

    def test_service_edit_page_renders_for_staff_user(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("service_edit", args=[self.service.pk]))
        self.assertEqual(response.status_code, 200)

    def test_staff_edit_page_renders_for_staff_user(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("staff_edit", args=[self.staff.pk]))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_create_customer_account_from_admin_view(self):
        self.client.force_login(self.admin_user)
        payload = {
            "first_name": "Ana",
            "last_name": "Lopez",
            "username": "analopez",
            "email": "ana@example.com",
            "password": "secret123",
            "confirm_password": "secret123",
            "address": "456 Oak Ave",
        }

        response = self.client.post(reverse("customer_add"), payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="analopez").exists())
        self.assertTrue(Customer.objects.filter(user__username="analopez").exists())

    def test_admin_can_create_staff_account_from_admin_view(self):
        self.client.force_login(self.admin_user)
        payload = {
            "first_name": "Mina",
            "last_name": "Santos",
            "username": "mina",
            "email": "mina@example.com",
            "password": "secret123",
            "confirm_password": "secret123",
            "position": "Receptionist",
        }

        response = self.client.post(reverse("staff_add"), payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="mina").exists())
        self.assertTrue(Staff.objects.filter(user__username="mina").exists())

    def test_admin_can_update_queue_number_on_appointment(self):
        self.client.force_login(self.admin_user)
        payload = {
            "customer": self.customer.pk,
            "staff": self.staff.pk,
            "service": self.service.pk,
            "date": "2026-07-11",
            "time": "10:00:00",
            "status": "Waiting",
            "queue_number": 42,
        }

        response = self.client.post(reverse("appointment_edit", args=[self.appointment.pk]), payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.queue_number, 42)

    def test_changing_the_date_gives_the_appointment_a_new_queue_number(self):
        appointment = Appointment.objects.create(
            customer=self.customer,
            staff=self.staff,
            service=self.service,
            date="2026-07-11",
            time="10:00:00",
            queue_number=7,
        )

        appointment.date = "2026-07-12"
        appointment.save()

        appointment.refresh_from_db()
        self.assertEqual(appointment.queue_number, 1)

    def test_services_short_url_redirects_to_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get("/services/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard/services/", response.url)
