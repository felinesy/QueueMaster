from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/book/', views.customer_book_appointment, name='customer_book_appointment'),
    path('customer/appointments/<int:pk>/reschedule/', views.customer_reschedule_appointment, name='customer_reschedule_appointment'),
    path('customer/appointments/<int:pk>/cancel/', views.customer_cancel_appointment, name='customer_cancel_appointment'),
    path('customer/history/', views.customer_history, name='customer_history'),
    path('customer/profile/', views.customer_profile, name='customer_profile'),
    path('customer/profile/edit/', views.customer_profile_edit, name='customer_profile_edit'),

    path('customers/', views.customer_list, name='customer_list'),
    path("customers/add/", views.customer_add, name="customer_add"),
    path("customers/edit/<int:pk>/", views.customer_edit, name="customer_edit"),
    path("customers/delete/<int:pk>/", views.customer_delete, name="customer_delete"),
    path("customers/toggle-active/<int:pk>/", views.customer_toggle_active, name="customer_toggle_active"),
    path('notifications/unread/', views.notifications_unread, name='notifications_unread'),
    path('notifications/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),
]