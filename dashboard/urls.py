from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

path("services/", views.service_list, name="service_list"),
path("services/add/", views.service_add, name="service_add"),
path("services/delete/<int:pk>/", views.service_delete, name="service_delete"),
path("appointments/", views.appointment_list, name="appointment_list"),
path("appointments/add/", views.appointment_add, name="appointment_add"),
path("appointments/delete/<int:pk>/", views.appointment_delete, name="appointment_delete"),
]