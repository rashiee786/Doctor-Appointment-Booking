from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import DoctorProfile,PatientProfile,Appointment,User,DoctorAvailability,DoctorRating
# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_verified')}),
    )

admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
admin.site.register(Appointment)
admin.site.register(DoctorAvailability)

@admin.register(DoctorRating)
class DoctorRatingAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "rating", "created_at")
    search_fields = ("doctor__user__username", "patient__username")



