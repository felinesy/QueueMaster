from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Service, Appointment
from .forms import ServiceForm, AppointmentForm, StaffForm

from accounts.models import Staff


@login_required
def dashboard(request):
    return render(request, "dashboard.html")


# =========================
# SERVICE
# =========================

def service_list(request):
    services = Service.objects.all()
    return render(request, "services/list.html", {
        "services": services
    })


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


def service_delete(request, pk):

    service = Service.objects.get(pk=pk)
    service.delete()

    return redirect("service_list")


# =========================
# APPOINTMENT
# =========================

def appointment_list(request):

    appointments = Appointment.objects.all()

    return render(request, "appointments/list.html", {
        "appointments": appointments
    })


def appointment_add(request):

    if request.method == "POST":

        form = AppointmentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("appointment_list")

    else:

        form = AppointmentForm()

    return render(request, "appointments/add.html", {
        "form": form
    })


def appointment_delete(request, pk):

    appointment = Appointment.objects.get(pk=pk)
    appointment.delete()

    return redirect("appointment_list")


# =========================
# STAFF
# =========================

def staff_list(request):

    staffs = Staff.objects.all()

    return render(request, "staff/list.html", {
        "staffs": staffs
    })


def staff_add(request):

    if request.method == "POST":

        form = StaffForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("staff_list")

    else:

        form = StaffForm()

    return render(request, "staff/add.html", {
        "form": form
    })


def staff_delete(request, pk):

    staff = Staff.objects.get(pk=pk)
    staff.delete()

    return redirect("staff_list")