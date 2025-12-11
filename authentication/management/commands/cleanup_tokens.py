from django.core.management.base import BaseCommand
from django.utils import timezone
from authentication.models import AuthToken, PasswordResetToken


class Command(BaseCommand):
    help = 'Clean up expired authentication and password reset tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()

        expired_auth_tokens = AuthToken.objects.filter(expires_at__lt=now, is_active=True)
        auth_count = expired_auth_tokens.count()

        expired_reset_tokens = PasswordResetToken.objects.filter(expires_at__lt=now, is_used=False)
        reset_count = expired_reset_tokens.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would delete {auth_count} expired auth tokens')
            )
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would delete {reset_count} expired password reset tokens')
            )
        else:
            expired_auth_tokens.update(is_active=False)

            expired_reset_tokens.delete()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully revoked {auth_count} expired auth tokens')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {reset_count} expired password reset tokens')
            )
