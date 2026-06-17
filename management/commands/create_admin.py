"""
Створює суперюзера автоматично при деплої, якщо його ще не існує.
Безпечно запускати багаторазово — не дублює і не падає з помилкою.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Створює суперюзера з env-переменных, якщо такого ще немає'

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write('DJANGO_SUPERUSER_USERNAME/PASSWORD не задані — пропускаємо')
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Суперюзер "{username}" вже існує — пропускаємо')
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Суперюзер "{username}" створений!'))