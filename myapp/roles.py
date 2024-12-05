from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .models import Project, Task, Material, Equipment, CustomUser

def create_role_permissions():
    # Define roles
    roles = {
        'Admin': {
            'can_manage_users': True,
            'can_manage_roles': True,
            'can_manage_projects': True,
            'can_manage_tasks': True,
            'can_manage_materials': True,
            'can_manage_equipment': True,
            'can_view_reports': True,
            'can_export_data': True,
        },
        'Project Manager': {
            'can_manage_projects': True,
            'can_manage_tasks': True,
            'can_manage_materials': True,
            'can_manage_equipment': True,
            'can_view_reports': True,
            'can_export_data': True,
        },
        'Worker': {
            'can_view_projects': True,
            'can_update_tasks': True,
            'can_view_materials': True,
            'can_use_equipment': True,
            'can_view_reports': False,
        },
        'Viewer': {
            'can_view_projects': True,
            'can_view_tasks': True,
            'can_view_materials': True,
            'can_view_equipment': True,
            'can_view_reports': False,
        }
    }

    # Create permissions for each model
    models_permissions = {
        Project: ['view', 'add', 'change', 'delete'],
        Task: ['view', 'add', 'change', 'delete'],
        Material: ['view', 'add', 'change', 'delete'],
        Equipment: ['view', 'add', 'change', 'delete'],
        CustomUser: ['view', 'add', 'change', 'delete'],
    }

    for model, actions in models_permissions.items():
        content_type = ContentType.objects.get_for_model(model)
        for action in actions:
            codename = f'{action}_{model._meta.model_name}'
            name = f'Can {action} {model._meta.verbose_name}'
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type,
            )

    # Create custom permissions
    custom_permissions = [
        ('can_export_data', 'Can export data from the system'),
        ('can_view_reports', 'Can view system reports'),
        ('can_manage_roles', 'Can manage user roles'),
    ]

    app_content_type = ContentType.objects.get_for_model(CustomUser)
    for codename, name in custom_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=app_content_type,
        )

    # Create groups and assign permissions
    for role_name, role_permissions in roles.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        
        # Clear existing permissions
        group.permissions.clear()
        
        # Assign model permissions based on role
        for model, actions in models_permissions.items():
            content_type = ContentType.objects.get_for_model(model)
            model_name = model._meta.model_name
            
            for action in actions:
                if role_name == 'Admin' or \
                   (role_name == 'Project Manager' and f'can_manage_{model_name}s' in role_permissions) or \
                   (role_name == 'Worker' and f'can_update_{model_name}s' in role_permissions) or \
                   (role_name == 'Viewer' and f'can_view_{model_name}s' in role_permissions):
                    permission = Permission.objects.get(
                        codename=f'{action}_{model_name}',
                        content_type=content_type,
                    )
                    group.permissions.add(permission)

        # Assign custom permissions based on role permissions
        for perm_name, has_perm in role_permissions.items():
            if has_perm and perm_name in [p[0] for p in custom_permissions]:
                permission = Permission.objects.get(codename=perm_name)
                group.permissions.add(permission)

def assign_role_to_user(user, role_name):
    """
    Assign a role (group) to a user
    """
    try:
        group = Group.objects.get(name=role_name)
        user.groups.clear()  # Remove existing groups
        user.groups.add(group)
        return True
    except Group.DoesNotExist:
        return False

def get_user_permissions(user):
    """
    Get all permissions for a user
    """
    if user.is_superuser:
        return Permission.objects.all()
    
    return user.user_permissions.all() | Permission.objects.filter(group__user=user)
