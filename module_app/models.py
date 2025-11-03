from django.db import models
from django.contrib.auth.models import User
from module_config_type_app.models import ModuleConfigType

class Module(models.Model):
    name = models.CharField(max_length=255)
    module_config = models.ForeignKey(ModuleConfigType, on_delete=models.PROTECT)
    
    STATUS_CHOICES = [
        ('New', 'New'),
        ('ATP_1_Pending', 'ATP 1 Pending'),
        ('ATP_1_Complete', 'ATP 1 Complete'),
        ('ESS_Pending', 'ESS Pending'),
        ('ESS_Complete', 'ESS Complete'),
        ('ATP_2_Pending', 'ATP 2 Pending'),
        ('ATP_2_Complete', 'ATP 2 Complete'),
        ('Shipped', 'Shipped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')

    def __str__(self):
        return self.name

class ATPReport(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='atp_reports')
    
    TEST_PHASE_CHOICES = [
        ('ATP_1', 'ATP 1'),
        ('ATP_2', 'ATP 2'),
    ]
    test_phase = models.CharField(max_length=5, choices=TEST_PHASE_CHOICES)
    
    report_file = models.FileField(upload_to='atp_reports/')
    qa_signoff = models.BooleanField(default=False)
    signed_off_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ATP Report for {self.module.name} - {self.test_phase}"

class ESSReport(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='ess_reports')
    report_file = models.FileField(upload_to='ess_reports/')
    qa_signoff = models.BooleanField(default=False)
    signed_off_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ESS Report for {self.module.name}"
