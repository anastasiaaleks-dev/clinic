# accounts/urls.py
from django.urls import path
from .views import register_patient, user_login, patient_dashboard, doctor_dashboard, make_appointment, user_logout, edit_appointment_patient, edit_appointment_doctor, delete_appointment, patient_profile, doctor_profile

urlpatterns = [
    path('register/', register_patient, name='register_patient'),
    path('login/', user_login, name='login'),
    path('dashboard/patient/', patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/<int:patient_id>/', doctor_dashboard, name='doctor_dashboard'),
    path('appointment/new/', make_appointment, name='make_appointment'),
    path('logout/', user_logout, name='logout'),
    path('edit-appointment/patient/<int:appointment_id>/', edit_appointment_patient, name='edit_appointment_patient'),
    path('edit-appointment/doctor/<int:appointment_id>/', edit_appointment_doctor, name='edit_appointment_doctor'),
    path('delete-appointment/<int:appointment_id>/', delete_appointment, name='delete_appointment'),
    path('patient-profile/', patient_profile, name='patient_profile'),
    path('doctor-profile/', doctor_profile, name='doctor_profile'),
]
