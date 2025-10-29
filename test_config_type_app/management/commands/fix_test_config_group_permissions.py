from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from test_config_type_app.models import TestConfigType


class Command(BaseCommand):
    help = 'Verify and fix mng_test_config_type group permissions'

    def handle(self, *args, **options):
        # Get the content type for TestConfigType model
        test_config_type_content_type = ContentType.objects.get_for_model(TestConfigType)

        # Get or create the group
        test_config_group, created = Group.objects.get_or_create(name='mng_test_config_type')
        
        if created:
            self.stdout.write(f"Created group: {test_config_group.name}")
        else:
            self.stdout.write(f"Found existing group: {test_config_group.name}")

        # Get all permissions for the TestConfigType model
        test_config_permissions = Permission.objects.filter(content_type=test_config_type_content_type)

        # Add all permissions to the group
        for perm in test_config_permissions:
            test_config_group.permissions.add(perm)
            self.stdout.write(f"Added permission: {perm.codename}")

        test_config_group.save()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated permissions for group "{test_config_group.name}"')
        )

        # Check users in the group
        users_in_group = test_config_group.user_set.all()
        self.stdout.write(f"Users in group: {list(users_in_group.values_list('username', flat=True))}")