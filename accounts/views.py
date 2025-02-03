from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden
from .models import User, Appointment, PatientProfile, DoctorProfile
from .forms import PatientRegistrationForm, AppointmentForm


# Главная страница
def index(request):
    if request.user.is_authenticated:
        if request.user.role == 'doctor':
            return redirect('doctor_profile')
        elif request.user.role == 'patient':
            return redirect('patient_profile')
    return render(request, 'index.html')


# Регистрация пациента
def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'patient'
            user.save()

            # Создаем профиль пациента
            PatientProfile.objects.create(
                user=user,
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                patronymic=form.cleaned_data.get('patronymic'),
                date_of_birth=form.cleaned_data.get('date_of_birth'),
                email=form.cleaned_data.get('email'),
            )

            login(request, user)
            return redirect('patient_profile')
    else:
        form = PatientRegistrationForm()
    return render(request, 'register.html', {'form': form})


# Вход
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'doctor':
                return redirect('doctor_profile')
            elif user.role == 'patient':
                return redirect('patient_profile')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# Выход
def user_logout(request):
    logout(request)
    return redirect('/')

# Личный кабинет пациента
@login_required
def patient_profile(request):
    # Получаем профиль текущего пациента
    profile = PatientProfile.objects.get(user=request.user)
    return render(request, 'patient_profile.html', {'profile': profile})


# Записи пациента
@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return HttpResponseForbidden("Доступ запрещен.")
    appointments = request.user.appointments.all()
    return render(request, 'patient_dashboard.html', {'appointments': appointments})

# Личный кабинет доктора
@login_required
def doctor_profile(request):
    # Получаем профиль текущего врача
    try:
        doctor_profile = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Профиль врача не найден.'})

    # Получение уникальных пациентов, записанных к врачу
    appointments = Appointment.objects.filter(doctor=request.user).select_related('patient')
    unique_patients = set()
    for appointment in appointments:
        unique_patients.add(appointment.patient.patient_profile)

    return render(request, 'doctor_profile.html', {
        'doctor_profile': doctor_profile,
        'patients': unique_patients
    })

# Записи пациента к доктору
@login_required
def doctor_dashboard(request, patient_id):
    patient_profile = get_object_or_404(PatientProfile, id=patient_id)
    return render(request, 'doctor_dashboard.html', {'patient_profile': patient_profile})


# Запись на прием
@login_required
def make_appointment(request):
    if request.user.role != 'patient':
        return HttpResponseForbidden("Доступ запрещен.")
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm()
    return render(request, 'make_appointment.html', {'form': form})

@login_required
def edit_appointment_patient(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('patient_dashboard')  # Перенаправить на страницу с личным кабинетом пациента
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'edit_appointment_patient.html', {'form': form})

@login_required
def edit_appointment_doctor(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('doctor_dashboard', appointment.patient.patient_profile.id)  # Перенаправить на страницу с личным кабинетом доктора
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'edit_appointment_doctor.html', {'form': form, 'appointment': appointment})

@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Проверка, чтобы только соответствующий пользователь мог удалять запись
    if request.user == appointment.patient or request.user == appointment.doctor:
        appointment.delete()
        if request.user.groups.filter(name='Doctor').exists():
            return redirect('doctor_dashboard', appointment.patient.id)  # Перенаправление в личный кабинет доктора
        return redirect('patient_dashboard')  # Перенаправление в личный кабинет пациента
    else:
        return redirect('home')  # Перенаправление на главную в случае попытки несанкционированного удаления
