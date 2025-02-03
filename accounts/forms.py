# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, PatientProfile, Appointment

class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="Имя", required=True)
    last_name = forms.CharField(label="Фамилия", required=True)
    patronymic = forms.CharField(label="Отчество", required=False)
    date_of_birth = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={'type': 'text', 'placeholder': 'DD.MM.YYYY'}),
        input_formats=['%d.%m.%Y']  # Ожидаемый формат даты
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name', 'patronymic', 'date_of_birth']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                patronymic=self.cleaned_data['patronymic'],
                date_of_birth=self.cleaned_data['date_of_birth'],
            )
        return user

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'doctor', 'appointment_date', 'num_of_sexual_partners',
            'first_sexual_intercourse', 'num_pregnancies', 
            'condylomatosis', 'smoking', 'smoking_years',
            'hormonal_contraception', 'hormonal_years', 'iud', 'iud_years',
            'hiv', 'schiller_test'
        ]
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'num_of_sexual_partners': forms.NumberInput(attrs={'class': 'form-control'}),
            'first_sexual_intercourse': forms.NumberInput(attrs={'class': 'form-control'}),
            'num_pregnancies': forms.NumberInput(attrs={'class': 'form-control'}),
            'condylomatosis': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smoking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smoking_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'hormonal_contraception': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hormonal_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'iud': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'iud_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'hiv': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'schiller_test': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('smoking'):
            cleaned_data['smoking_years'] = 0
        if not cleaned_data.get('hormonal_contraception'):
            cleaned_data['hormonal_years'] = 0
        if not cleaned_data.get('iud'):
            cleaned_data['iud_years'] = 0
        return cleaned_data
