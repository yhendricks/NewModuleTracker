from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pcb_test_result_app.models import PcbTestResult, QaSignoff


class Command(BaseCommand):
    help = 'Set up permissions for the add_board_bringup_result and qa_signoff_board_bringup_result groups'

    def handle(self, *args, **options):
        # Get or create the add_board_bringup_result group (existing functionality)
        add_group, created = Group.objects.get_or_create(name='add_board_bringup_result')
        
        # Get the content type for PcbTestResult model
        pcb_test_result_content_type = ContentType.objects.get_for_model(PcbTestResult)
        
        # Add permissions to the add_board_bringup_result group
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
                add_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {perm_codename} does not exist for add_board_bringup_result')
                )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created group "add_board_bringup_result" with all permissions')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated group "add_board_bringup_result" with all permissions')
            )
        
        # Create or get the QA signoff group
        qa_group, created = Group.objects.get_or_create(name='qa_signoff_board_bringup_result')
        
        # Get the content type for QaSignoff model
        qa_signoff_content_type = ContentType.objects.get_for_model(QaSignoff)
        
        # Add permissions to the qa_signoff_board_bringup_result group
        qa_permissions_to_add = [
            'add_qasignoff',
            'change_qasignoff',
            'view_qasignoff',
            'view_pcbtestresult',  # Allow viewing test results
        ]
        
        for perm_codename in qa_permissions_to_add:
            try:
                # Try to find permission in both content types
                try:
                    perm = Permission.objects.get(
                        content_type=qa_signoff_content_type,
                        codename=perm_codename
                    )
                except Permission.DoesNotExist:
                    # If not in QaSignoff content type, try PcbTestResult content type
                    perm = Permission.objects.get(
                        content_type=pcb_test_result_content_type,
                        codename=perm_codename
                    )
                
                qa_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {perm_codename} does not exist for qa_signoff_board_bringup_result')
                )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created group "qa_signoff_board_bringup_result" with all permissions')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated group "qa_signoff_board_bringup_result" with all permissions')
            )