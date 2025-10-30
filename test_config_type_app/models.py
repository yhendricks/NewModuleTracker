from django.db import models
from django.contrib.auth.models import Group


class TestConfigType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Test Config Type"
        verbose_name_plural = "Test Config Types"
        ordering = ['name']


class TestStep(models.Model):
    STEP_TYPES = [
        ('VOLTAGE', 'Voltage Measurement'),
        ('CURRENT', 'Current Measurement'),
        ('RESISTANCE', 'Resistance Measurement'),
        ('FREQUENCY', 'Frequency Measurement'),
        ('QUESTION', 'Yes/No Question'),
        ('INSTRUCTION', 'Instruction/User Action'),
    ]
    
    test_config = models.ForeignKey(TestConfigType, on_delete=models.CASCADE, related_name='steps')
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    order = models.PositiveIntegerField()
    
    # For measurements
    parameter_name = models.CharField(max_length=100, blank=True, null=True)
    min_value = models.FloatField(blank=True, null=True)
    max_value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=10, blank=True, null=True)
    
    # For questions
    question_text = models.CharField(max_length=500, blank=True, null=True)
    required_answer = models.BooleanField(default=True)  # True for 'Yes', False for 'No'
    
    # For instructions
    instruction_text = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.step_type == 'VOLTAGE':
            return f"Voltage: {self.parameter_name} ({self.min_value}V - {self.max_value}V)"
        elif self.step_type == 'CURRENT':
            return f"Current: {self.parameter_name} ({self.min_value}A - {self.max_value}A)"
        elif self.step_type == 'RESISTANCE':
            return f"Resistance: {self.parameter_name} ({self.min_value}ohm - {self.max_value}ohm)"
        elif self.step_type == 'FREQUENCY':
            return f"Frequency: {self.parameter_name} ({self.min_value}Hz - {self.max_value}Hz)"
        elif self.step_type == 'QUESTION':
            required = "Yes" if self.required_answer else "No"
            return f"Question: {self.question_text} (Answer: {required})"
        elif self.step_type == 'INSTRUCTION':
            return f"Instruction: {self.instruction_text}"
        else:
            return f"Step {self.order}: {self.get_step_type_display()}"

    class Meta:
        verbose_name = "Test Step"
        verbose_name_plural = "Test Steps"
        ordering = ['test_config', 'order']