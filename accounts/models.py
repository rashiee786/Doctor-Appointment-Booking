from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    email = models.EmailField(unique=True)  
    is_verified = models.BooleanField(default=False)

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=[("M","Male"),("F","Female")], blank=True)
    dob = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)       
    profile_image = models.ImageField(upload_to="patient_profiles/", blank=True, null=True)

    def __str__(self):
        return self.user.username

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    consultation_fee = models.DecimalField(max_digits=6, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    image = models.ImageField(upload_to="doctors/", blank=True, null=True)

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return 0

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"
    
class Appointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_as_patient")
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="appointments_as_doctor")
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} → Dr. {self.doctor.user.username} on {self.date} {self.time}"

class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="availabilities")
    day_of_week = models.IntegerField(choices=[
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"),
        (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday"),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()


class DoctorRating(models.Model):
    doctor = models.ForeignKey("DoctorProfile", on_delete=models.CASCADE, related_name="ratings")
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=1)  
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "patient") 

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.rating}⭐"



