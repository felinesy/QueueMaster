from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from dashboard import views as dashboard_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('services/', RedirectView.as_view(url='/dashboard/services/'), name='service_list_shortcut'),
    path('services/add/', RedirectView.as_view(url='/dashboard/services/add/'), name='service_add_shortcut'),
    path('appointments/', RedirectView.as_view(url='/dashboard/appointments/'), name='appointment_list_shortcut'),
    path('appointments/add/', RedirectView.as_view(url='/dashboard/appointments/add/'), name='appointment_add_shortcut'),
    path('staff/', RedirectView.as_view(url='/dashboard/staff/'), name='staff_list_shortcut'),
    path('staff/add/', RedirectView.as_view(url='/dashboard/staff/add/'), name='staff_add_shortcut'),
    path('customers/', RedirectView.as_view(url='/dashboard/customers/'), name='customer_list_shortcut'),
    path('customers/add/', RedirectView.as_view(url='/dashboard/customers/add/'), name='customer_add_shortcut'),
]