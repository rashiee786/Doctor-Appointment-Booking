from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .forms import RegisterForm,AvailabilityForm,PatientProfileForm,DoctorProfileForm,DoctorRatingForm
from .models import PatientProfile, DoctorProfile, Appointment,DoctorAvailability,DoctorRating
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from datetime import datetime, date, time as dtime
from django.views.decorators.http import require_POST
from django.contrib import messages

# Create your views here.

def home(request):
    doctors = DoctorProfile.objects.filter(is_approved=True)
    return render(request, 'home.html', {'doctors': doctors})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_verified = False   
            user.save()
            
            if user.role == 'PATIENT':
                PatientProfile.objects.create(user=user)
            elif user.role == 'DOCTOR':
                DoctorProfile.objects.create(user=user, is_approved=False)
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user and user.is_active:
            login(request, user)

            if user.role == 'DOCTOR':
                return redirect('accounts:doctor_dashboard')
            elif user.role == 'PATIENT':
                return redirect('accounts:patient_dashboard')
            elif user.role == 'ADMIN':
                return redirect('/admin/')
            else:
                return redirect('accounts:home')
        else:
            return render(request, 'login.html', {"error": "Invalid username or password"})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')

def terms_view(request):
    return render(request, 'terms.html')

def privacy_view(request):
    return render(request, 'privacy.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        messages.success(request, "Thank you, your message has been received!")
        return redirect("accounts:contact")
    return render(request, "contact.html")

@login_required
def doctor_dashboard(request):
    doctor = DoctorProfile.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor)

    total_appointments = appointments.count()
    confirmed_count = appointments.filter(status="CONFIRMED").count()
    cancelled_count = appointments.filter(status="CANCELLED").count()
    completed_count = appointments.filter(status="COMPLETED").count()

    context = {
        "doctor": doctor,
        "appointments": appointments,
        "total_appointments": total_appointments,
        "confirmed_count": confirmed_count,
        "cancelled_count": cancelled_count,
        "completed_count": completed_count,
    }
    return render(request, "doctor_dashboard.html", context)

def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by("-created_at")
    return render(request, "patient_dashboard.html", {"appointments": appointments})

@login_required
def book_appointment(request):
    if not hasattr(request.user, "role") or request.user.role != "PATIENT":
        return HttpResponseForbidden("Only patients can book appointments.")

    doctors = DoctorProfile.objects.filter(is_approved=True)
    doctor = None
    slots = None

    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")
        notes = request.POST.get("notes", "")

        doctor = get_object_or_404(DoctorProfile, id=doctor_id, is_approved=True)

        try:
            chosen_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            chosen_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return render(request, "appointment.html", {
                "doctors": doctors,
                "today": date.today().isoformat(),
                "error": "Invalid date or time format."
            })

        if chosen_date < date.today():
            return render(request, "appointment.html", {
                "doctors": doctors,
                "today": date.today().isoformat(),
                "error": "You cannot book appointments for past dates."
            })

        weekday = chosen_date.weekday()  
        day_slots = DoctorAvailability.objects.filter(doctor=doctor, day_of_week=weekday)
        valid = any(slot.start_time <= chosen_time <= slot.end_time for slot in day_slots)

        if not valid:
            return render(request, "appointment.html", {
                "doctors": doctors,
                "today": date.today().isoformat(),
                "error": "Doctor not available at this time."
            })

        appt = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=chosen_date,
            time=chosen_time,
            notes=notes,
            status="CONFIRMED" 
        )

        messages.success(request, "Your appointment has been booked successfully.")
        return redirect("accounts:appointment_confirmation", appt_id=appt.id)

    else:
        doctor_id = request.GET.get("doctor_id")
        if doctor_id:
            doctor = get_object_or_404(DoctorProfile, id=doctor_id, is_approved=True)
            slots = doctor.availabilities.all()

    return render(request, "appointment.html", {
        "doctors": doctors,
        "doctor": doctor,
        "slots": slots,
        "today": date.today().isoformat()
    })

@login_required
def appointment_confirmation(request, appt_id):
    appointment = get_object_or_404(Appointment, id=appt_id, patient=request.user)
    return render(request, "appointment_confirmation.html", {"appointment": appointment})
        
@login_required
def appointment_detail(request, appt_id):
    appointment = get_object_or_404(Appointment, id=appt_id, patient=request.user)
    return render(request, "appointment_detail.html", {"appointment": appointment})

def doctors_list(request):
    query = request.GET.get("q")
    doctors = DoctorProfile.objects.filter(is_approved=True)
    if query:
        doctors = doctors.filter(
            Q(specialization__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )
    return render(request, "doctors.html", {"doctors": doctors})

def speciality_list(request):
    specialities = (
        DoctorProfile.objects
        .filter(is_approved=True)
        .values_list("specialization", flat=True)
        .distinct()
        .order_by("specialization")
    )
    return render(request, "speciality_list.html", {"specialities": specialities})

def speciality_doctors(request, speciality):
    query = request.GET.get("q")
    doctors = DoctorProfile.objects.filter(
        is_approved=True,
        specialization__iexact=speciality
    )
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )
    return render(request, "speciality_doctors.html", {
        "speciality": speciality,
        "doctors": doctors
    })

@login_required
def edit_patient_profile(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = PatientProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:patient_dashboard")
    else:
        form = PatientProfileForm(instance=profile, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        })
    return render(request, "patient_profile_edit.html", {"form": form})

@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if request.method == "POST":
        appointment.delete()
        return redirect("accounts:patient_dashboard")
    return render(request, "confirm_delete.html", {"appointment": appointment})

@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    if request.method == "POST":
        date_str = request.POST.get("date")
        time_str = request.POST.get("time")
        notes = request.POST.get("notes")

        try:
            appointment.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            appointment.time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return render(request, "edit_appointment", {
                "appointment": appointment,
                "error": "Invalid date or time format."
            })

        appointment.notes = notes
        appointment.save()
        return redirect("accounts:patient_dashboard")

    return render(request, "edit_appointment.html", {"appointment": appointment})


@login_required
@require_POST
def appointment_action(request, pk):
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor_profile)

    action = request.POST.get("action")  # CONFIRMED, CANCELLED, COMPLETED
    notes = request.POST.get("notes", "").strip()

    if action in ["CONFIRMED", "CANCELLED", "COMPLETED"]:
        appointment.status = action
        if notes:
            appointment.notes = notes
        appointment.save()

    return redirect("accounts:doctor_dashboard")


@login_required
def availability_list(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    availabilities = doctor.availabilities.all()
    return render(request, "availability_list.html", {"availabilities": availabilities})

@login_required
def availability_create(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    if request.method == "POST":
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.doctor = doctor
            availability.save()
            return redirect("accounts:availability_list")
    else:
        form = AvailabilityForm()
    return render(request, "availability_form.html", {"form": form})

@login_required
@require_POST
def availability_delete(request, pk):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    availability = get_object_or_404(DoctorAvailability, pk=pk, doctor=doctor)
    availability.delete()
    return redirect("accounts:availability_list")


@login_required
def edit_doctor_profile(request):
    profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = DoctorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor profile updated successfully.")
            return redirect("accounts:doctor_dashboard")
    else:
        form = DoctorProfileForm(instance=profile, initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        })
    return render(request, "doctor_profile_edit.html", {"form": form})


@login_required
def rate_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)

    has_completed = Appointment.objects.filter(
        doctor=doctor, patient=request.user, status="COMPLETED"
    ).exists()
    if not has_completed:
        messages.error(request, "You can only rate a doctor after completing an appointment.")
        return redirect("accounts:speciality_doctors", speciality=doctor.specialization)

    if request.method == "POST":
        form = DoctorRatingForm(request.POST)
        if form.is_valid():
            DoctorRating.objects.update_or_create(
                doctor=doctor,
                patient=request.user,
                defaults=form.cleaned_data
            )
            messages.success(request, "Your rating has been submitted!")
            return redirect("accounts:speciality_doctors", speciality=doctor.specialization)
    else:
        form = DoctorRatingForm()
    return render(request, "rate_doctor.html", {"form": form, "doctor": doctor})
