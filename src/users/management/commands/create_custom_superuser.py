from datetime import datetime


from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create a superuser with custom options'

    def handle(self, *args, **options):
        User = get_user_model()

        username = input('Username: ')
        email = input('E-mail: ')
        password = input('Password:')

        user = User.objects.create_superuser(username=username, email=email, password=password, phone='123456789',
                                             birth_date=datetime.fromisoformat('1990-12-04'),
                                             status='ACTIVE')
        self.stdout.write(self.style.SUCCESS(f'Superuser "{user} created successfully.'))
