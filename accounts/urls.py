"""
URL configuration for medbook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts import views   # import from accounts app
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings



app_name = 'accounts'  

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("specialities/", views.speciality_list, name="speciality_list"),
    path("specialities/<str:speciality>/", views.speciality_doctors, name="speciality_doctors"),
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("patient/dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path("appointments/book/", views.book_appointment, name="book_appointment"),
    path("confirmation/<int:appt_id>/", views.appointment_confirmation, name="appointment_confirmation"),
    path("doctors/", views.doctors_list, name="doctors"),
    path("patient/profile/edit/", views.edit_patient_profile, name="edit_patient_profile"),  
    path("appointments/delete/<int:appointment_id>/", views.delete_appointment, name="delete_appointment"),
    path("appointments/edit/<int:appointment_id>/", views.edit_appointment, name="edit_appointment"),
    path("appointment/<int:appt_id>/", views.appointment_detail, name="appointment_detail"),
    path("doctor/appointment/<int:pk>/action/", views.appointment_action, name="appointment_action"),
    path("doctor/profile/edit/", views.edit_doctor_profile, name="edit_doctor_profile"),
    path("doctor/availability/", views.availability_list, name="availability_list"),
    path("doctor/availability/new/", views.availability_create, name="availability_create"),
    path("doctor/availability/<int:pk>/delete/", views.availability_delete, name="availability_delete"),
    path("rate-doctor/<int:doctor_id>/", views.rate_doctor, name="rate_doctor"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
