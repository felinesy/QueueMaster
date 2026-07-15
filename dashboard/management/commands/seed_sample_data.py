from datetime import timedelta

from django.contrib.auth.models import User as AuthUser
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Customer, Staff
from dashboard.models import Appointment, Service


class Command(BaseCommand):
    help = "Create sample salon customers, staff, services, and appointments for UI testing"

    def handle(self, *args, **options):
        customer_names = [
            ("Mika", "Santos"),
            ("Janelle", "Ramos"),
            ("Rafael", "Dela Cruz"),
            ("Ariana", "Bautista"),
            ("Nico", "Fernandez"),
            ("Princess", "Villanueva"),
            ("Ethan", "Cabrera"),
            ("Bianca", "Sarmiento"),
            ("Ken", "Lobregat"),
            ("Lia", "Tuazon"),
        ]
        staff_names = [
            ("Althea", "Gonzales"),
            ("Martin", "Tan"),
            ("Clara", "Mendoza"),
            ("Jude", "Abarquez"),
            ("Dianne", "Patalinghog"),
        ]
        cebu_addresses = [
            "Cebu City, Cebu",
            "Mandaue City, Cebu",
            "Lapu-Lapu City, Cebu",
            "Talisay City, Cebu",
            "Naga City, Cebu",
            "Danao City, Cebu",
            "Minglanilla, Cebu",
            "Carcar City, Cebu",
            "Bogo City, Cebu",
            "Consolacion, Cebu",
        ]
        service_data = [
            ("Haircut & Blow Dry", "Classic salon haircut with blow dry finish", 450.00, 45),
            ("Hair Color Refresh", "Root touch-up or color refresh service", 1200.00, 90),
            ("Manicure & Pedicure", "Spa-style nail care for hands and feet", 650.00, 60),
            ("Facial Glow Treatment", "Deep cleansing and skin rejuvenation facial", 900.00, 75),
            ("Hair Styling for Event", "Elegant styling for special occasions", 850.00, 60),
            ("Keratin Treatment", "Smoothening treatment for frizz-free hair", 1800.00, 120),
            ("Nail Art Design", "Creative nail art for special events", 500.00, 45),
            ("Bridal Makeup Trial", "Soft glam look for wedding preparation", 1600.00, 90),
        ]

        self.stdout.write("Creating sample salon data...")

        admin_user, admin_created = AuthUser.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if admin_created:
            admin_user.set_password("Password123!")
            admin_user.save(update_fields=["password", "is_staff", "is_superuser"])
            self.stdout.write("Created admin account: admin")
        else:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save(update_fields=["is_staff", "is_superuser"])

        for index, (first_name, last_name) in enumerate(customer_names):
            username = f"customer{index + 1}"
            user, created = AuthUser.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": f"{username}@example.com",
                },
            )
            if created:
                user.set_password("Password123!")
                user.save(update_fields=["password"])
            customer, customer_created = Customer.objects.get_or_create(
                user=user,
                defaults={"address": cebu_addresses[index % len(cebu_addresses)]},
            )
            if customer_created:
                self.stdout.write(f"Created customer: {customer}")

        for index, (first_name, last_name) in enumerate(staff_names):
            username = f"staff{index + 1}"
            user, created = AuthUser.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": f"{username}@example.com",
                },
            )
            if created:
                user.set_password("Password123!")
                user.save(update_fields=["password"])
            staff, staff_created = Staff.objects.get_or_create(
                user=user,
                defaults={"position": "Senior Stylist" if index % 2 == 0 else "Beauty Specialist"},
            )
            if staff_created:
                self.stdout.write(f"Created staff: {staff}")

        for service_name, description, price, duration in service_data:
            service, created = Service.objects.get_or_create(
                service_name=service_name,
                defaults={
                    "description": description,
                    "price": price,
                    "duration": duration,
                },
            )
            if created:
                self.stdout.write(f"Created service: {service}")

        customers = list(Customer.objects.all())
        staff_members = list(Staff.objects.all())
        services = list(Service.objects.all())

        if not customers or not staff_members or not services:
            self.stdout.write(self.style.WARNING("Not enough data to create appointments. Please rerun after creating customers, staff, and services."))
            return

        today = timezone.localdate()
        appointment_payloads = [
            {"customer": customers[0], "staff": staff_members[0], "service": services[0], "date": today, "time": "09:30:00", "status": "Waiting"},
            {"customer": customers[1], "staff": staff_members[1], "service": services[1], "date": today, "time": "10:15:00", "status": "Serving"},
            {"customer": customers[2], "staff": staff_members[2], "service": services[2], "date": today, "time": "11:00:00", "status": "Pending"},
            {"customer": customers[3], "staff": staff_members[3], "service": services[3], "date": today, "time": "13:00:00", "status": "Completed"},
            {"customer": customers[4], "staff": staff_members[0], "service": services[4], "date": today, "time": "14:30:00", "status": "Cancelled"},
            {"customer": customers[5], "staff": staff_members[1], "service": services[5], "date": today, "time": "15:15:00", "status": "Waiting"},
            {"customer": customers[6], "staff": staff_members[2], "service": services[6], "date": today + timedelta(days=1), "time": "09:45:00", "status": "Pending"},
            {"customer": customers[7], "staff": staff_members[3], "service": services[7], "date": today + timedelta(days=1), "time": "12:30:00", "status": "Waiting"},
            {"customer": customers[8], "staff": staff_members[4], "service": services[0], "date": today + timedelta(days=1), "time": "10:00:00", "status": "Serving"},
            {"customer": customers[9], "staff": staff_members[0], "service": services[2], "date": today + timedelta(days=2), "time": "14:00:00", "status": "Completed"},
            {"customer": customers[1], "staff": staff_members[1], "service": services[3], "date": today + timedelta(days=2), "time": "11:30:00", "status": "Pending"},
            {"customer": customers[3], "staff": staff_members[2], "service": services[5], "date": today + timedelta(days=2), "time": "16:00:00", "status": "Waiting"},
            {"customer": customers[2], "staff": staff_members[3], "service": services[4], "date": today + timedelta(days=3), "time": "09:00:00", "status": "Waiting"},
            {"customer": customers[4], "staff": staff_members[4], "service": services[6], "date": today + timedelta(days=3), "time": "10:45:00", "status": "Pending"},
            {"customer": customers[6], "staff": staff_members[0], "service": services[1], "date": today + timedelta(days=3), "time": "13:15:00", "status": "Completed"},
            {"customer": customers[8], "staff": staff_members[1], "service": services[7], "date": today + timedelta(days=4), "time": "12:00:00", "status": "Waiting"},
            {"customer": customers[0], "staff": staff_members[2], "service": services[3], "date": today + timedelta(days=4), "time": "15:30:00", "status": "Serving"},
            {"customer": customers[5], "staff": staff_members[3], "service": services[2], "date": today + timedelta(days=4), "time": "16:45:00", "status": "Pending"},
            {"customer": customers[7], "staff": staff_members[4], "service": services[0], "date": today + timedelta(days=5), "time": "08:30:00", "status": "Waiting"},
            {"customer": customers[9], "staff": staff_members[0], "service": services[5], "date": today + timedelta(days=5), "time": "10:30:00", "status": "Completed"},
            {"customer": customers[2], "staff": staff_members[1], "service": services[6], "date": today + timedelta(days=5), "time": "14:15:00", "status": "Pending"},
        ]

        for payload in appointment_payloads:
            appointment, created = Appointment.objects.get_or_create(
                customer=payload["customer"],
                date=payload["date"],
                time=payload["time"],
                defaults={
                    "staff": payload["staff"],
                    "service": payload["service"],
                    "status": payload["status"],
                },
            )
            if created:
                self.stdout.write(f"Created appointment: {appointment}")
            else:
                appointment.status = payload["status"]
                appointment.staff = payload["staff"]
                appointment.service = payload["service"]
                appointment.save(update_fields=["status", "staff", "service"])

        self.stdout.write(self.style.SUCCESS("Sample salon data created successfully."))
