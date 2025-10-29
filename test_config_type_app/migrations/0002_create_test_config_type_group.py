from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_test_config_type_group(apps, schema_editor):
    """Create the mng_test_config_type group and assign permissions"""
    # We need to use the historical version of the models
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    TestConfigType = apps.get_model('test_config_type_app', 'TestConfigType')

    # Get the content type for TestConfigType model
    test_config_type_content_type = ContentType.objects.get_for_model(TestConfigType)

    # Create the group
    test_config_group, created = Group.objects.get_or_create(name='mng_test_config_type')

    # Get the permissions
    permissions = Permission.objects.filter(
        content_type=test_config_type_content_type,
        codename__in=['add_testconfigtype', 'change_testconfigtype', 'delete_testconfigtype', 'view_testconfigtype']
    )

    # Add permissions to the group
    for perm in permissions:
        test_config_group.permissions.add(perm)


def remove_test_config_type_group(apps, schema_editor):
    """Remove the mng_test_config_type group"""
    Group = apps.get_model('auth', 'Group')
    test_config_group = Group.objects.filter(name='mng_test_config_type')
    if test_config_group.exists():
        test_config_group.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('test_config_type_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_test_config_type_group, remove_test_config_type_group),
    ]