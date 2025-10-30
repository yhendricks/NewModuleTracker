from django.db import models
from django.contrib.auth.models import Group
from pcb_type_app.models import PcbType
from test_config_type_app.models import TestConfigType


class Batch(models.Model):
    """Represents a batch of PCBs with common properties"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    pcb_type = models.ForeignKey(PcbType, on_delete=models.CASCADE, related_name='batches')
    test_config_type = models.ForeignKey(TestConfigType, on_delete=models.CASCADE, related_name='batches')
    hardware_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Batch"
        verbose_name_plural = "Batches"
        ordering = ['name']


class Pcb(models.Model):
    """Represents a single PCB with unique serial number"""
    serial_number = models.CharField(max_length=100, unique=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='pcbs')
    hardware_modified = models.BooleanField(default=False)
    modified_hardware_version = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.serial_number} ({self.batch.name})"

    @property
    def effective_hardware_version(self):
        """Return the effective hardware version (modified version if applicable, otherwise batch version)"""
        if self.hardware_modified and self.modified_hardware_version:
            return self.modified_hardware_version
        return self.batch.hardware_version

    class Meta:
        verbose_name = "PCB"
        verbose_name_plural = "PCBs"
        ordering = ['serial_number']


# Create the management group for batches
def create_batch_management_group():
    """Create the mng_batches group with proper permissions"""
    batch_group, created = Group.objects.get_or_create(name='mng_batches')
    return batch_group