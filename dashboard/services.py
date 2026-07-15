from datetime import time

from django.db.models import Max, Count


def next_queue_number_for_date(service_date):
    from .models import Appointment

    latest_queue = (
        Appointment.objects.filter(date=service_date)
        .aggregate(max_queue=Max("queue_number"))
        .get("max_queue")
        or 0
    )
    return latest_queue + 1


def appointment_summary():
    from .models import Appointment

    counts = Appointment.objects.values("status").annotate(total=Count("id"))
    summary = {"Pending": 0, "Waiting": 0, "Serving": 0, "Completed": 0, "Cancelled": 0}

    for item in counts:
        summary[item["status"]] = item["total"]

    return summary


def get_business_hours():
    from .models import BusinessHours

    hours = BusinessHours.objects.first()
    if hours is not None:
        return hours
    return BusinessHours(open_time=time(9, 0), close_time=time(17, 0))


def is_closed_date(selected_date):
    from .models import ClosedDay

    return ClosedDay.objects.filter(date=selected_date).exists()


def get_closed_dates():
    from .models import ClosedDay

    return list(ClosedDay.objects.order_by("date").values_list("date", flat=True))
