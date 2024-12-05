from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from myapp.models import Task, Project, Material, Equipment, CustomUser

class Command(BaseCommand):
    help = 'Sets up role-based access control by creating groups and assigning permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        pm_group, _ = Group.objects.get_or_create(name='Project Manager')
        worker_group, _ = Group.objects.get_or_create(name='Worker')
        viewer_group, _ = Group.objects.get_or_create(name='Viewer')

        # Get content types
        task_ct = ContentType.objects.get_for_model(Task)
        project_ct = ContentType.objects.get_for_model(Project)
        material_ct = ContentType.objects.get_for_model(Material)
        equipment_ct = ContentType.objects.get_for_model(Equipment)
        user_ct = ContentType.objects.get_for_model(CustomUser)

        # Define permissions for each model
        task_permissions = Permission.objects.filter(content_type=task_ct)
        project_permissions = Permission.objects.filter(content_type=project_ct)
        material_permissions = Permission.objects.filter(content_type=material_ct)
        equipment_permissions = Permission.objects.filter(content_type=equipment_ct)
        user_permissions = Permission.objects.filter(content_type=user_ct)

        # Admin permissions (all permissions)
        admin_permissions = list(task_permissions) + list(project_permissions) + \
                          list(material_permissions) + list(equipment_permissions) + \
                          list(user_permissions)
        admin_group.permissions.set(admin_permissions)
        self.stdout.write(self.style.SUCCESS('Admin permissions set'))

        # Project Manager permissions
        pm_permissions = []
        # Task permissions
        pm_permissions.extend(task_permissions)
        # Project permissions (view and change only)
        pm_permissions.extend(project_permissions.filter(codename__in=['view_project', 'change_project']))
        # Material and equipment permissions (view only)
        pm_permissions.extend(material_permissions.filter(codename__in=['view_material']))
        pm_permissions.extend(equipment_permissions.filter(codename__in=['view_equipment']))
        pm_group.permissions.set(pm_permissions)
        self.stdout.write(self.style.SUCCESS('Project Manager permissions set'))

        # Worker permissions
        worker_permissions = []
        # Task permissions (view and change only)
        worker_permissions.extend(task_permissions.filter(codename__in=['view_task', 'change_task']))
        # Project, material, and equipment permissions (view only)
        worker_permissions.extend(project_permissions.filter(codename__in=['view_project']))
        worker_permissions.extend(material_permissions.filter(codename__in=['view_material']))
        worker_permissions.extend(equipment_permissions.filter(codename__in=['view_equipment']))
        worker_group.permissions.set(worker_permissions)
        self.stdout.write(self.style.SUCCESS('Worker permissions set'))

        # Viewer permissions (view only for all models)
        viewer_permissions = []
        viewer_permissions.extend(task_permissions.filter(codename__in=['view_task']))
        viewer_permissions.extend(project_permissions.filter(codename__in=['view_project']))
        viewer_permissions.extend(material_permissions.filter(codename__in=['view_material']))
        viewer_permissions.extend(equipment_permissions.filter(codename__in=['view_equipment']))
        viewer_group.permissions.set(viewer_permissions)
        self.stdout.write(self.style.SUCCESS('Viewer permissions set'))

        self.stdout.write(self.style.SUCCESS('Successfully set up all roles and permissions'))
