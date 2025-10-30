from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from batch_app.models import Batch, Pcb


class Command(BaseCommand):
    help = 'Verify and fix mng_batches group permissions'

    def handle(self, *args, **options):
        # Get the content types for Batch and Pcb models
        batch_content_type = ContentType.objects.get_for_model(Batch)
        pcb_content_type = ContentType.objects.get_for_model(Pcb)

        # Get or create the group
        batch_group, created = Group.objects.get_or_create(name='mng_batches')
        
        if created:
            self.stdout.write(f"Created group: {batch_group.name}")
        else:
            self.stdout.write(f"Found existing group: {batch_group.name}")

        # Get all permissions for the Batch model
        batch_permissions = Permission.objects.filter(content_type=batch_content_type)

        # Get all permissions for the Pcb model
        pcb_permissions = Permission.objects.filter(content_type=pcb_content_type)

        # Add all permissions to the group
        for perm in batch_permissions:
            batch_group.permissions.add(perm)
            self.stdout.write(f"Added permission: {perm.codename}")

        for perm in pcb_permissions:
            batch_group.permissions.add(perm)
            self.stdout.write(f"Added permission: {perm.codename}")

        batch_group.save()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated permissions for group "{batch_group.name}"')
        )

        # Check users in the group
        users_in_group = batch_group.user_set.all()
        self.stdout.write(f"Users in group: {list(users_in_group.values_list('username', flat=True))}")