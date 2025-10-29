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


class VoltageMeasurement(models.Model):
    test_config = models.ForeignKey(TestConfigType, on_delete=models.CASCADE, related_name='voltage_measurements')
    parameter_name = models.CharField(max_length=100)
    min_value = models.FloatField()
    max_value = models.FloatField()
    unit = models.CharField(max_length=10, default='V')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.min_value}V - {self.max_value}V"

    class Meta:
        verbose_name = "Voltage Measurement"
        verbose_name_plural = "Voltage Measurements"


class CurrentMeasurement(models.Model):
    test_config = models.ForeignKey(TestConfigType, on_delete=models.CASCADE, related_name='current_measurements')
    parameter_name = models.CharField(max_length=100)
    min_value = models.FloatField()
    max_value = models.FloatField()
    unit = models.CharField(max_length=10, default='A')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.min_value}A - {self.max_value}A"

    class Meta:
        verbose_name = "Current Measurement"
        verbose_name_plural = "Current Measurements"


class YesNoQuestion(models.Model):
    test_config = models.ForeignKey(TestConfigType, on_delete=models.CASCADE, related_name='yes_no_questions')
    question_text = models.CharField(max_length=200)
    required_answer = models.BooleanField(default=True)  # True for 'Yes', False for 'No'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        required = "Yes" if self.required_answer else "No"
        return f"{self.question_text} (Answer: {required})"

    class Meta:
        verbose_name = "Yes/No Question"
        verbose_name_plural = "Yes/No Questions"


class ResistanceMeasurement(models.Model):
    test_config = models.ForeignKey(TestConfigType, on_delete=models.CASCADE, related_name='resistance_measurements')
    parameter_name = models.CharField(max_length=100)
    min_value = models.FloatField()
    max_value = models.FloatField()
    unit = models.CharField(max_length=10, default='Ω')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.min_value}Ω - {self.max_value}Ω"

    class Meta:
        verbose_name = "Resistance Measurement"
        verbose_name_plural = "Resistance Measurements"


class FrequencyMeasurement(models.Model):
    test_config = models.ForeignKey(TestConfigType, on_delete=models.CASCADE, related_name='frequency_measurements')
    parameter_name = models.CharField(max_length=100)
    min_value = models.FloatField()
    max_value = models.FloatField()
    unit = models.CharField(max_length=10, default='Hz')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.min_value}Hz - {self.max_value}Hz"

    class Meta:
        verbose_name = "Frequency Measurement"
        verbose_name_plural = "Frequency Measurements"