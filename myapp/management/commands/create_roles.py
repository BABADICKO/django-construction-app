from django.core.management.base import BaseCommand
from myapp.roles import create_role_permissions

class Command(BaseCommand):
    help = 'Create default roles and permissions'

    def handle(self, *args, **options):
        try:
            create_role_permissions()
            self.stdout.write(self.style.SUCCESS('Successfully created roles and permissions'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating roles and permissions: {str(e)}'))
