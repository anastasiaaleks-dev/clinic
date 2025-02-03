from django.core.management.commands import createsuperuser
from django.utils.translation import gettext_lazy as _

class Command(createsuperuser.Command):
    help = 'Creates a superuser without needing a username.'

    def add_arguments(self, parser):
        # Убираем обязательность поля username
        super().add_arguments(parser)
        parser.remove_argument('username')

    def handle(self, *args, **options):
        # Перезаписываем метод handle, чтобы он не требовал username
        options['username'] = options['email']
        super().handle(*args, **options)
