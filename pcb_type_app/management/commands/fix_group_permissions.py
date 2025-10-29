from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from pcb_type_app.models import PcbType


class Command(BaseCommand):
    help = 'Verify and fix mng_pcb_type group permissions'

    def handle(self, *args, **options):
        # Get the content type for PcbType model
        pcb_type_content_type = ContentType.objects.get_for_model(PcbType)

        # Get or create the group
        pcb_group, created = Group.objects.get_or_create(name='mng_pcb_type')
        
        if created:
            self.stdout.write(f"Created group: {pcb_group.name}")
        else:
            self.stdout.write(f"Found existing group: {pcb_group.name}")

        # Get all permissions for the PcbType model
        pcb_permissions = Permission.objects.filter(content_type=pcb_type_content_type)

        # Add all permissions to the group
        for perm in pcb_permissions:
            pcb_group.permissions.add(perm)
            self.stdout.write(f"Added permission: {perm.codename}")

        pcb_group.save()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated permissions for group "{pcb_group.name}"')
        )

        # Check users in the group
        users_in_group = pcb_group.user_set.all()
        self.stdout.write(f"Users in group: {list(users_in_group.values_list('username', flat=True))}")