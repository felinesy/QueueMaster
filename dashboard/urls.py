from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    path("services/", views.service_list, name="service_list"),
    path("services/add/", views.service_add, name="service_add"),
    path("services/edit/<int:pk>/", views.service_edit, name="service_edit"),
    path("services/delete/<int:pk>/", views.service_delete, name="service_delete"),
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/add/", views.appointment_add, name="appointment_add"),
    path("appointments/edit/<int:pk>/", views.appointment_edit, name="appointment_edit"),
    path("appointments/delete/<int:pk>/", views.appointment_delete, name="appointment_delete"),
    path("appointments/status/<int:pk>/<str:status>/", views.appointment_status_update, name="appointment_status_update"),
    path("settings/", views.business_settings, name="business_settings"),
    path("settings/closed-day/delete/<int:pk>/", views.closed_day_delete, name="closed_day_delete"),

    path("staff/", views.staff_list, name="staff_list"),
    path("staff/add/", views.staff_add, name="staff_add"),
    path("staff/edit/<int:pk>/", views.staff_edit, name="staff_edit"),
    path("staff/delete/<int:pk>/", views.staff_delete, name="staff_delete"),
    path("staff/toggle-active/<int:pk>/", views.staff_toggle_active, name="staff_toggle_active"),
]
