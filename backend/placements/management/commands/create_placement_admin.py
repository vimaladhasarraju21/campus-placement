from django.core.management.base import BaseCommand
from placements.models import User


class Command(BaseCommand):
    help = 'Creates a placement admin (placement cell) account.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--password', required=True)
        parser.add_argument('--email', default='')

    def handle(self, *args, **options):
        username = options['username']
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists.'))
            return
        user = User.objects.create_user(
            username=username,
            password=options['password'],
            email=options['email'],
            role=User.ROLE_ADMIN,
            is_staff=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Placement admin "{user.username}" created.'))
