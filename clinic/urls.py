# clinic/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),  # Главная страница
    path('', include('accounts.urls')),  # Подключаем маршруты из приложения accounts
]
