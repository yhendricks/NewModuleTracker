from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def assign_permissions_to_group(apps, schema_editor):
    """Assign permissions to the mng_test_config_type group"""
    # Get the Group and Permission models as they exist at the time of this migration
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    TestConfigType = apps.get_model('test_config_type_app', 'TestConfigType')

    # Get the content type for TestConfigType model
    try:
        test_config_type_content_type = ContentType.objects.get(app_label='test_config_type_app', model='testconfigtype')
    except ContentType.DoesNotExist:
        # If ContentType doesn't exist yet, try to get it by looking for the model
        test_config_type_content_type = ContentType.objects.get_for_model(TestConfigType)

    # Get or create the group
    test_config_group, created = Group.objects.get_or_create(name='mng_test_config_type')

    # Get all permissions for the TestConfigType model
    test_config_permissions = Permission.objects.filter(content_type=test_config_type_content_type)

    # Add all permissions for the TestConfigType to the group
    for perm in test_config_permissions:
        test_config_group.permissions.add(perm)

    # Try to get TestStep model and its permissions if it exists at this migration state
    try:
        TestStep = apps.get_model('test_config_type_app', 'TestStep')
        try:
            test_step_content_type = ContentType.objects.get(app_label='test_config_type_app', model='teststep')
        except ContentType.DoesNotExist:
            # If ContentType doesn't exist yet, try to get it by looking for the model
            test_step_content_type = ContentType.objects.get_for_model(TestStep)

        # Get all permissions for the TestStep model
        test_step_permissions = Permission.objects.filter(content_type=test_step_content_type)
        
        # Add all permissions for the TestStep to the group
        for perm in test_step_permissions:
            test_config_group.permissions.add(perm)
    except LookupError:
        # TestStep model doesn't exist yet at this migration state, skip adding TestStep permissions
        pass


def remove_permissions_from_group(apps, schema_editor):
    """Remove permissions from the mng_test_config_type group"""
    Group = apps.get_model('auth', 'Group')
    test_config_group = Group.objects.filter(name='mng_test_config_type').first()
    if test_config_group:
        test_config_group.permissions.clear()


class Migration(migrations.Migration):

    dependencies = [
        ('test_config_type_app', '0002_create_test_config_type_group'),
    ]

    operations = [
        migrations.RunPython(assign_permissions_to_group, remove_permissions_from_group),
    ]