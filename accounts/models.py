# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth import get_user_model
from .units import calculate_risk

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Создание и сохранение пользователя с email вместо username.
        """
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создание суперпользователя с email вместо username.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # Отключаем username
    email = models.EmailField(unique=True)  # Email как основной идентификатор
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"

class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patients', limit_choices_to={'role': 'doctor'})
    appointment_date = models.DateField(verbose_name="Дата приема")
    num_of_sexual_partners = models.IntegerField(verbose_name="Количество половых партнеров", null=True, blank=True)
    first_sexual_intercourse = models.IntegerField(verbose_name="Возраст начала половой жизни", null=True, blank=True)
    num_pregnancies = models.IntegerField(verbose_name="Количество беременностей", null=True, blank=True)
    condylomatosis = models.BooleanField(verbose_name="Замечали ли вы у себя папилломы?", null=True, blank=True, default=False)
    smoking = models.BooleanField(verbose_name="Курение", default=False)
    smoking_years = models.IntegerField(verbose_name="Стаж курения (в годах)", null=True, blank=True, default=0)
    hormonal_contraception = models.BooleanField(verbose_name="Гормональная контрацепция", default=False)
    hormonal_years = models.IntegerField(verbose_name="Продолжительность гормональной контрацепции (в годах)",null=True, blank=True, default=0)
    iud = models.BooleanField(verbose_name="Внутриматочная спираль", default=False)
    iud_years = models.IntegerField(verbose_name="Продолжительность ношения внутриматочной спирали (в годах)", null=True, blank=True, default=0)
    hiv = models.BooleanField(verbose_name="Наличие ВИЧ", null=True, blank=True)
    schiller_test = models.BooleanField(verbose_name="Подозрительный результат Шиллер-теста", null=True, blank=True)
    risk_class = models.CharField(max_length=50, default='')
    risk = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Запись: {self.patient.email} к {self.doctor.email}"

    def save(self, *args, **kwargs):
        if not self.smoking:
            self.smoking_years = 0
        if not self.hormonal_contraception:
            self.hormonal_years = 0
        if not self.iud:
            self.iud_years = 0
        # Вычисление риска при создании записи
        self.risk_class, self.risk = calculate_risk(self)
        super().save(*args, **kwargs)
