from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from accounts.models import User


class Command(BaseCommand):
    help = 'Unsuspend users who have an expired suspension.'

    def handle(self, *args, **kwargs):
        users = User.objects.filter(active=2, bandate__lt=now().date())
        users.update(active=0)
        for user in users:
            user.save()
        self.stdout.write(self.style.SUCCESS(
            'Successfully cleaned expired suspensions.'))
