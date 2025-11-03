from django.db import models
from pcb_type_app.models import PcbType

class ModuleConfigType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    pcbs = models.ManyToManyField(PcbType, through='ModuleConfigPcb', related_name='module_configs')

    def __str__(self):
        return self.name

class ModuleConfigPcb(models.Model):
    module_config_type = models.ForeignKey(ModuleConfigType, on_delete=models.CASCADE)
    pcb_type = models.ForeignKey(PcbType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('module_config_type', 'pcb_type')

    def __str__(self):
        return f"{self.quantity} x {self.pcb_type.name} in {self.module_config_type.name}"
