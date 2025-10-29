from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_pcb_type_group(apps, schema_editor):
    """Create the mng_pcb_type group and assign permissions"""
    # We need to use the historical version of the models
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    PcbType = apps.get_model('pcb_type_app', 'PcbType')

    # Get the content type for PcbType model
    pcb_type_content_type = ContentType.objects.get_for_model(PcbType)

    # Create the group
    pcb_group, created = Group.objects.get_or_create(name='mng_pcb_type')

    # Get the permissions
    permissions = Permission.objects.filter(
        content_type=pcb_type_content_type,
        codename__in=['add_pcbtype', 'change_pcbtype', 'delete_pcbtype', 'view_pcbtype']
    )

    # Add permissions to the group
    for perm in permissions:
        pcb_group.permissions.add(perm)


def remove_pcb_type_group(apps, schema_editor):
    """Remove the mng_pcb_type group"""
    Group = apps.get_model('auth', 'Group')
    pcb_group = Group.objects.filter(name='mng_pcb_type')
    if pcb_group.exists():
        pcb_group.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pcb_type_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_pcb_type_group, remove_pcb_type_group),
    ]