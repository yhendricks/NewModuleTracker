from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def assign_permissions_to_group(apps, schema_editor):
    """Assign permissions to the mng_pcb_type group"""
    # Get the Group and Permission models as they exist at the time of this migration
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    PcbType = apps.get_model('pcb_type_app', 'PcbType')

    # Get the content type for PcbType model
    try:
        pcb_type_content_type = ContentType.objects.get(app_label='pcb_type_app', model='pcbtype')
    except ContentType.DoesNotExist:
        # If ContentType doesn't exist yet, try to get it by looking for the model
        pcb_type_content_type = ContentType.objects.get_for_model(PcbType)

    # Get or create the group
    pcb_group, created = Group.objects.get_or_create(name='mng_pcb_type')

    # Get all permissions for the PcbType model
    pcb_permissions = Permission.objects.filter(content_type=pcb_type_content_type)

    # Add all permissions to the group
    for perm in pcb_permissions:
        pcb_group.permissions.add(perm)


def remove_permissions_from_group(apps, schema_editor):
    """Remove permissions from the mng_pcb_type group"""
    Group = apps.get_model('auth', 'Group')
    pcb_group = Group.objects.filter(name='mng_pcb_type').first()
    if pcb_group:
        pcb_group.permissions.clear()


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_type_app', '0002_create_pcb_type_group'),
    ]

    operations = [
        migrations.RunPython(assign_permissions_to_group, remove_permissions_from_group),
    ]