import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create/update an admin (superuser) from env vars"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("ADMIN_USERNAME")
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD not set. Skipping create_admin."
            ))
            return

        user = User.objects.filter(username=username).first() or User.objects.filter(email=email).first()

        if user is None:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS("Created admin user."))
        else:
            user.username = username
            user.email = email
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            self.stdout.write(self.style.SUCCESS("Updated admin user."))
