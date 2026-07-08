from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Service
from .forms import ServiceForm
from django.shortcuts import render, redirect
from .models import Service, Appointment
from .forms import ServiceForm, AppointmentForm


@login_required
def dashboard(request):
    return render(request, "dashboard.html")

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