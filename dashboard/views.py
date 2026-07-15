from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Customer, Staff
from accounts.decorators import staff_required, admin_required

from .models import Service, Appointment, BusinessHours, ClosedDay
from .forms import (
    ServiceForm,
    AppointmentForm,
    AdminStaffForm,
    AdminStaffEditForm,
    BusinessHoursForm,
    ClosedDayForm,
)
from .services import appointment_summary, get_business_hours

@staff_required
def dashboard(request):

    customer_count = Customer.objects.count()
    staff_count = Staff.objects.count()
    service_count = Service.objects.count()
    appointment_count = Appointment.objects.count()
    queue_summary = appointment_summary()
    today = timezone.localdate()
    today_appointment_count = Appointment.objects.filter(date=today).count()
    pending_approval_count = Appointment.objects.filter(status="Pending").count()
    active_queue_count = Appointment.objects.filter(status__in=["Waiting", "Serving"]).count()

    recent_appointments = Appointment.objects.select_related(
        "customer",
        "staff",
        "service"
    ).order_by("-date", "-time")[:5]

    context = {
        "customer_count": customer_count,
        "staff_count": staff_count,
        "service_count": service_count,
        "appointment_count": appointment_count,
        "waiting_count": queue_summary["Waiting"],
        "serving_count": queue_summary["Serving"],
        "completed_count": queue_summary["Completed"],
        "today_appointment_count": today_appointment_count,
        "pending_approval_count": pending_approval_count,
        "active_queue_count": active_queue_count,
        "recent_appointments": recent_appointments,
    }

    return render(request, "dashboard.html", context)


@admin_required
def admin_dashboard(request):

    customer_count = Customer.objects.count()
    staff_count = Staff.objects.count()
    service_count = Service.objects.count()
    appointment_count = Appointment.objects.count()
    queue_summary = appointment_summary()
    today = timezone.localdate()
    today_appointment_count = Appointment.objects.filter(date=today).count()
    pending_approval_count = Appointment.objects.filter(status="Pending").count()
    active_queue_count = Appointment.objects.filter(status__in=["Waiting", "Serving"]).count()

    recent_appointments = Appointment.objects.select_related(
        "customer",
        "staff",
        "service"
    ).order_by("-date", "-time")[:5]

    return render(request, "admin_dashboard.html", {
        "customer_count": customer_count,
        "staff_count": staff_count,
        "service_count": service_count,
        "appointment_count": appointment_count,
        "waiting_count": queue_summary["Waiting"],
        "serving_count": queue_summary["Serving"],
        "completed_count": queue_summary["Completed"],
        "today_appointment_count": today_appointment_count,
        "pending_approval_count": pending_approval_count,
        "active_queue_count": active_queue_count,
        "recent_appointments": recent_appointments,
    })


@staff_required
def business_settings(request):
    db_ready = True
    try:
        business_hours = BusinessHours.objects.first()
    except DatabaseError:
        db_ready = False
        business_hours = BusinessHours()

    if request.method == "POST" and db_ready:
        if "save_hours" in request.POST:
            hours_form = BusinessHoursForm(request.POST, instance=business_hours)
            closed_form = ClosedDayForm()
            if hours_form.is_valid():
                hours_form.save()
                messages.success(request, "Operating hours updated successfully.")
                return redirect("business_settings")
        elif "add_closed_day" in request.POST:
            hours_form = BusinessHoursForm(instance=business_hours)
            closed_day_pk = request.POST.get("closed_day_pk")
            if closed_day_pk:
                closed_day = get_object_or_404(ClosedDay, pk=closed_day_pk)
                closed_form = ClosedDayForm(request.POST, instance=closed_day)
            else:
                closed_form = ClosedDayForm(request.POST)

            if closed_form.is_valid():
                closed_form.save()
                if closed_day_pk:
                    messages.success(request, "Closed date updated successfully.")
                else:
                    messages.success(request, "Closed date added successfully.")
                return redirect("business_settings")
    else:
        hours_form = BusinessHoursForm(instance=business_hours)
        closed_form = ClosedDayForm()

    if db_ready:
        closed_days = ClosedDay.objects.order_by("date")
    else:
        closed_days = []
        messages.warning(request, "Database migration is not applied yet. Please run migrate to enable settings.")

    return render(request, "settings.html", {
        "hours_form": hours_form,
        "closed_form": closed_form,
        "closed_days": closed_days,
        "business_hours": business_hours,
        "db_ready": db_ready,
    })


@staff_required
def closed_day_delete(request, pk):
    closed_day = get_object_or_404(ClosedDay, pk=pk)
    closed_day.delete()
    messages.success(request, "Closed date removed.")
    return redirect("business_settings")


# =========================
# SERVICE
# =========================

@staff_required
def service_list(request):

    services = Service.objects.all()

    return render(request, "services/list.html", {
        "services": services
    })
@staff_required
def service_add(request):

    if request.method == "POST":

        form = ServiceForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("service_list")

    else:

        form = ServiceForm()

    return render(request, "services/add.html", {
        "form": form
    })


@staff_required
def service_edit(request, pk):

    service = get_object_or_404(Service, pk=pk)

    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)

        if form.is_valid():
            form.save()
            return redirect("service_list")
    else:
        form = ServiceForm(instance=service)

    return render(request, "services/add.html", {
        "form": form,
        "title": "Edit Service",
        "button_label": "Update Service",
    })


@staff_required
def service_delete(request, pk):

    service = Service.objects.get(pk=pk)
    service.delete()

    return redirect("service_list")


# =========================
# APPOINTMENT
# =========================

@staff_required
def appointment_list(request):

    status = request.GET.get("status", "").strip()
    selected_date = request.GET.get("date", "").strip()
    appointments = Appointment.objects.select_related("customer", "staff", "service").all()

    valid_statuses = [choice[0] for choice in Appointment.STATUS_CHOICES]
    if status and status in valid_statuses:
        appointments = appointments.filter(status=status)

    if selected_date:
        appointments = appointments.filter(date=selected_date)

    available_dates = Appointment.objects.order_by("date").values_list("date", flat=True).distinct()

    return render(request, "appointments/list.html", {
        "appointments": appointments,
        "current_status": status,
        "current_date": selected_date,
        "status_choices": valid_statuses,
        "available_dates": available_dates,
    })


@staff_required
def appointment_add(request):

    if request.method == "POST":

        form = AppointmentForm(request.POST)

        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.save()
            return redirect("appointment_list")

    else:

        form = AppointmentForm()

    return render(request, "appointments/add.html", {
        "form": form
    })


@staff_required
def appointment_edit(request, pk):

    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)

        if form.is_valid():
            form.save()
            return redirect("appointment_list")

    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "appointments/add.html", {
        "form": form,
        "title": "Edit Appointment",
        "button_label": "Update Appointment",
    })


@staff_required
def appointment_delete(request, pk):

    appointment = Appointment.objects.get(pk=pk)
    appointment.delete()

    return redirect("appointment_list")


@staff_required
def appointment_status_update(request, pk, status):

    appointment = get_object_or_404(Appointment, pk=pk)
    valid_statuses = {choice[0] for choice in Appointment.STATUS_CHOICES}

    if status in valid_statuses:
        appointment.status = status
        appointment.save(update_fields=["status"])
        messages.success(request, f"Appointment status updated to {status}.")
    else:
        messages.error(request, "That appointment status is not supported.")

    return redirect("appointment_list")


# =========================
# STAFF
# =========================

@admin_required
def staff_list(request):

    staffs = []
    users = User.objects.filter(is_staff=True, is_superuser=False)
    for user in users:
        staff = Staff.objects.filter(user=user).first()
        if staff is None:
            staff = Staff.objects.create(user=user, position="Staff")
        staffs.append(staff)

    return render(request, "staff/list.html", {
        "staffs": staffs
    })


@admin_required
def staff_add(request):

    if request.method == "POST":

        form = AdminStaffForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("staff_list")

    else:

        form = AdminStaffForm()

    return render(request, "staff/add.html", {
        "form": form
    })


@admin_required
def staff_edit(request, pk):

    staff = get_object_or_404(Staff, pk=pk)

    if request.method == "POST":
        form = AdminStaffEditForm(request.POST, staff=staff)

        if form.is_valid():
            form.save()
            return redirect("staff_list")
    else:
        form = AdminStaffEditForm(staff=staff)

    return render(request, "staff/add.html", {
        "form": form,
        "title": "Edit Staff",
        "button_label": "Update Staff",
    })


@admin_required
def staff_delete(request, pk):

    staff = Staff.objects.get(pk=pk)
    staff.delete()

    return redirect("staff_list")


@admin_required
def staff_toggle_active(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    user = staff.user
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    if user.is_active:
        messages.success(request, "Staff account reactivated.")
    else:
        messages.success(request, "Staff account suspended.")

    return redirect("staff_list")