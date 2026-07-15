from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Customer, Notification
from .forms import (
    CustomerForm,
    CustomerProfileForm,
    CustomerAppointmentForm,
    CustomerAppointmentEditForm,
    AdminCustomerForm,
    AdminCustomerEditForm,
)
from .decorators import staff_required, admin_required
from dashboard.models import Appointment, Service
from dashboard.services import get_business_hours, get_closed_dates


def get_customer_profile(user):
    customer, _created = Customer.objects.get_or_create(user=user)
    return customer


def register_view(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        role = request.POST.get("role", "customer")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        if username in getattr(settings, "ADMIN_USERNAMES", set()):
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["is_staff", "is_superuser"])
        elif role == "staff":
            user.is_staff = True
            user.save(update_fields=["is_staff"])
            from .models import Staff as StaffModel
            StaffModel.objects.create(user=user, position="Staff")
        else:
            Customer.objects.create(user=user)

        messages.success(request, "Registration successful.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        role = request.POST.get("role", "customer")
        if user is not None:

            if role == "customer" and (user.is_staff or user.is_superuser):
                messages.error(request, "Please use staff login for this account.")
            elif role == "staff" and not (user.is_staff or user.is_superuser):
                messages.error(request, "Please use customer login for this account.")
            else:
                login(request, user)

                if user.is_superuser:
                    return redirect("admin_dashboard")

                return redirect("dashboard")

        else:

            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def logout_view(request):

    logout(request)

    return redirect("login")


@login_required(login_url="login")
def customer_dashboard(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect("dashboard")

    customer = get_customer_profile(request.user)
    appointments = []

    appointments = Appointment.objects.select_related("service", "staff").filter(customer=customer).order_by("-date", "-time")

    active_appointment = appointments.filter(status__in=["Waiting", "Serving"]).first()

    upcoming_appointments = appointments.exclude(status__in=["Completed", "Cancelled"])[:3]

    return render(request, "customer/dashboard.html", {
        "customer": customer,
        "appointments": appointments,
        "upcoming_appointments": upcoming_appointments,
        "active_appointment": active_appointment,
    })


@login_required(login_url="login")
def customer_book_appointment(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect("dashboard")

    customer = get_customer_profile(request.user)

    if request.method == "POST":
        form = CustomerAppointmentForm(request.POST)

        if form.is_valid():
            selected_date = form.cleaned_data["date"]
            selected_time = form.cleaned_data["time"]

            if Appointment.objects.filter(
                customer=customer,
                date=selected_date,
                time=selected_time,
                status__in=["Waiting", "Serving"],
            ).exists():
                messages.error(request, "You already have an active appointment at that date and time.")
                return render(request, "customer/book_appointment.html", {
                    "form": form,
                    "business_hours": get_business_hours(),
                    "closed_days": get_closed_dates(),
                })

            appointment = form.save(commit=False)
            appointment.customer = customer
            appointment.status = "Pending"
            appointment.staff = None
            appointment.save()
            messages.success(request, f"Appointment submitted for approval. Your queue number is Q{appointment.queue_number:03d}.")
            return redirect("customer_history")

    else:
        form = CustomerAppointmentForm()

    return render(request, "customer/book_appointment.html", {
        "form": form,
        "business_hours": get_business_hours(),
        "closed_days": get_closed_dates(),
    })


@login_required(login_url="login")
def customer_reschedule_appointment(request, pk):

    if request.user.is_staff or request.user.is_superuser:
        return redirect("dashboard")

    customer = get_customer_profile(request.user)
    appointment = get_object_or_404(Appointment, pk=pk, customer=customer)

    if appointment.status in ["Completed", "Cancelled"]:
        messages.error(request, "Completed or cancelled appointments cannot be rescheduled.")
        return redirect("customer_history")

    if request.method == "POST":
        form = CustomerAppointmentEditForm(request.POST, instance=appointment)

        if form.is_valid():
            selected_date = form.cleaned_data["date"]
            selected_time = form.cleaned_data["time"]

            if Appointment.objects.filter(
                customer=customer,
                date=selected_date,
                time=selected_time,
                status__in=["Waiting", "Serving"],
            ).exclude(pk=appointment.pk).exists():
                messages.error(request, "You already have another active appointment at that date and time.")
                return render(request, "customer/reschedule_appointment.html", {
                    "appointment": appointment,
                    "form": form,
                    "business_hours": get_business_hours(),
                    "closed_days": get_closed_dates(),
                })

            form.save()
            messages.success(request, f"Appointment rescheduled. Your new queue number is Q{appointment.queue_number:03d}.")
            return redirect("customer_history")
    else:
        form = CustomerAppointmentEditForm(instance=appointment)

    return render(request, "customer/reschedule_appointment.html", {
        "appointment": appointment,
        "form": form,
        "business_hours": get_business_hours(),
        "closed_days": get_closed_dates(),
    })


@login_required(login_url="login")
def customer_cancel_appointment(request, pk):

    if request.user.is_staff or request.user.is_superuser:
        return redirect("dashboard")

    customer = get_customer_profile(request.user)
    appointment = get_object_or_404(Appointment, pk=pk, customer=customer)

    if appointment.status in ["Completed", "Cancelled"]:
        messages.error(request, "Completed or cancelled appointments cannot be canceled again.")
        return redirect("customer_history")

    appointment.status = "Cancelled"
    appointment.save(update_fields=["status"])
    messages.success(request, "Appointment canceled successfully.")
    return redirect("customer_history")


@login_required(login_url="login")
def customer_history(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect("dashboard")

    customer = get_customer_profile(request.user)
    status = request.GET.get("status", "").strip()
    appointments = Appointment.objects.select_related("service", "staff").filter(customer=customer).order_by("-date", "-time")

    valid_statuses = ["Pending", "Waiting", "Serving", "Completed", "Cancelled"]
    if status and status in valid_statuses:
        appointments = appointments.filter(status=status)

    return render(request, "customer/history.html", {
        "customer": customer,
        "appointments": appointments,
        "current_status": status,
        "status_choices": valid_statuses,
    })


@login_required(login_url="login")
def customer_profile(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect("dashboard")

    customer = get_customer_profile(request.user)
    return render(request, "customer/profile.html", {
        "customer": customer,
    })


@login_required(login_url="login")
def customer_profile_edit(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect("dashboard")

    customer = get_customer_profile(request.user)

    if request.method == "POST":
        profile_form = CustomerProfileForm(request.POST, instance=request.user)

        if profile_form.is_valid():
            new_password = request.POST.get("new_password", "").strip()
            confirm_password = request.POST.get("confirm_password", "").strip()

            if new_password:
                if new_password != confirm_password:
                    messages.error(request, "New password and confirmation do not match.")
                    return redirect("customer_profile_edit")

                request.user.set_password(new_password)
                update_session_auth_hash(request, request.user)

            profile_form.save()
            customer.address = request.POST.get("address", customer.address)
            customer.save(update_fields=["address"])

            messages.success(request, "Profile updated successfully.")
            return redirect("customer_profile")
    else:
        profile_form = CustomerProfileForm(instance=request.user)

    return render(request, "customer/profile_edit.html", {
        "customer": customer,
        "profile_form": profile_form,
    })

@admin_required
def customer_list(request):
    customers = []
    users = User.objects.filter(is_staff=False, is_superuser=False)
    for user in users:
        customer = Customer.objects.filter(user=user).first()
        if customer is None:
            customer = Customer.objects.create(user=user)
        customers.append(customer)
    return render(request, "customers/list.html", {
        "customers": customers
    })


@admin_required
def customer_add(request):

    if request.method == "POST":
        form = AdminCustomerForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("customer_list")

    else:
        form = AdminCustomerForm()

    return render(request, "customers/add.html", {
        "form": form
    })


@admin_required
def customer_edit(request, pk):

    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        form = AdminCustomerEditForm(request.POST, customer=customer)

        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = AdminCustomerEditForm(customer=customer)

    return render(request, "customers/add.html", {
        "form": form,
        "title": "Edit Customer",
        "button_label": "Update Customer",
    })


@admin_required
def customer_delete(request, pk):

    customer = Customer.objects.get(pk=pk)
    customer.delete()

    return redirect("customer_list")


@admin_required
def customer_toggle_active(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    user = customer.user
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    if user.is_active:
        messages.success(request, "Customer account reactivated.")
    else:
        messages.success(request, "Customer account suspended.")

    return redirect("customer_list")


@login_required
def notifications_unread(request):
    """Return unread notifications for the logged-in user as JSON."""
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    data = [
        {
            'id': n.id,
            'message': n.message,
            'level': n.level,
            'created_at': n.created_at.isoformat(),
        }
        for n in notifications
    ]
    return JsonResponse({'notifications': data})


@require_POST
@login_required
def notifications_mark_read(request):
    ids = request.POST.getlist('ids[]') or request.POST.getlist('ids')
    if ids:
        Notification.objects.filter(user=request.user, id__in=ids).update(is_read=True)
    return JsonResponse({'status': 'ok'})