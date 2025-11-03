from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pcb_test_result_app.models import PcbTestResult


class Command(BaseCommand):
    help = 'Set up permissions for the add_board_bringup_result group'

    def handle(self, *args, **options):
        # Get the group or create it
        group, created = Group.objects.get_or_create(name='add_board_bringup_result')
        
        # Get the content type for PcbTestResult model
        pcb_test_result_content_type = ContentType.objects.get_for_model(PcbTestResult)
        
        # Get all permissions for the PcbTestResult model
        pcb_test_result_permissions = Permission.objects.filter(
            content_type=pcb_test_result_content_type
        )
        
        # Add all permissions to the group
        for perm in pcb_test_result_permissions:
            group.permissions.add(perm)
        
        # Add specific permissions that might be needed
        permissions_to_add = [
            'add_pcbtestresult',
            'change_pcbtestresult',
            'delete_pcbtestresult',
            'view_pcbtestresult',
        ]
        
        for perm_codename in permissions_to_add:
            try:
                perm = Permission.objects.get(
                    content_type=pcb_test_result_content_type,
                    codename=perm_codename
                )
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {perm_codename} does not exist')
                )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created group "{group.name}" with all permissions')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated group "{group.name}" with all permissions')
            )