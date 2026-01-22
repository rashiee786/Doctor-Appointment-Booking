from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,PatientProfile,DoctorProfile,DoctorRating,DoctorAvailability

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"]) 
        if commit:
            user.save()
        return user

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailability
        fields = ['day_of_week', 'start_time', 'end_time']

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned

class PatientProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = PatientProfile
        fields = ["first_name", "last_name", "email", "phone", "gender", "dob", "location", "address", "profile_image"]

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile.save()
        return profile

class DoctorProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = DoctorProfile
        fields = ["first_name", "last_name", "email", "specialization", "consultation_fee", "image"]

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile.save()
        return profile

class DoctorRatingForm(forms.ModelForm):
    class Meta:
        model = DoctorRating
        fields = ["rating", "review"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "review": forms.Textarea(attrs={"rows": 3}),
        }
