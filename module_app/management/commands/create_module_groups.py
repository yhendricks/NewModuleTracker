from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Creates the required user groups with appropriate permissions'

    def handle(self, *args, **options):
        # Define the groups and their permissions
        groups_permissions = {
            'module_config_type': [
                'module_config_type_app.add_moduleconfigtype',
                'module_config_type_app.change_moduleconfigtype',
                'module_config_type_app.delete_moduleconfigtype',
                'module_config_type_app.view_moduleconfigtype',
            ],
            'module_test_group': [
                'module_app.add_module',
                'module_app.change_module',
                'module_app.view_module',
                'module_app.add_atpreport',
                'module_app.change_atpreport',
                'module_app.view_atpreport',
                'module_app.add_essreport',
                'module_app.change_essreport',
                'module_app.view_essreport',
            ],
            'qa_module_sign_off': [
                'module_app.change_atpreport',
                'module_app.change_essreport',
                'module_app.view_atpreport',
                'module_app.view_essreport',
                'module_app.view_module',
            ]
        }

        for group_name, permissions in groups_permissions.items():
            # Create or get the group
            group, created = Group.objects.get_or_create(name=group_name)
            
            # Get the permissions
            for perm_full_name in permissions:
                app_label, codename = perm_full_name.split('.')
                
                try:
                    permission = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                    group.permissions.add(permission)
                    self.stdout.write(f'Added permission {permission} to group {group_name}')
                except Permission.DoesNotExist:
                    self.stdout.write(f'Permission {codename} does not exist in app {app_label}')
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created successfully'))
            else:
                self.stdout.write(f'Group "{group_name}" updated with permissions')
        
        self.stdout.write(self.style.SUCCESS('Groups and permissions setup completed'))