from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from batch_app.models import Pcb


class PcbTestResult(models.Model):
    """Represents a test result for a specific PCB"""
    pcb = models.ForeignKey(Pcb, on_delete=models.CASCADE, related_name='test_results')
    technician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    # Overall test result
    PASSED = 'PASSED'
    FAILED = 'FAILED'
    INCOMPLETE = 'INCOMPLETE'
    TEST_RESULT_CHOICES = [
        (PASSED, 'Passed'),
        (FAILED, 'Failed'),
        (INCOMPLETE, 'Incomplete'),
    ]
    result = models.CharField(max_length=20, choices=TEST_RESULT_CHOICES, default=INCOMPLETE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Test Result for {self.pcb.serial_number} by {self.technician.username} on {self.test_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "PCB Test Result"
        verbose_name_plural = "PCB Test Results"
        ordering = ['-test_date']


class VoltageMeasurementResult(models.Model):
    """Represents a voltage measurement result"""
    test_result = models.ForeignKey(PcbTestResult, on_delete=models.CASCADE, related_name='voltage_measurements')
    parameter_name = models.CharField(max_length=100)
    measured_value = models.FloatField()
    unit = models.CharField(max_length=10, default='V')
    min_value = models.FloatField()  # Reference from test config
    max_value = models.FloatField()  # Reference from test config
    passed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.measured_value}{self.unit}"

    class Meta:
        verbose_name = "Voltage Measurement Result"
        verbose_name_plural = "Voltage Measurement Results"


class CurrentMeasurementResult(models.Model):
    """Represents a current measurement result"""
    test_result = models.ForeignKey(PcbTestResult, on_delete=models.CASCADE, related_name='current_measurements')
    parameter_name = models.CharField(max_length=100)
    measured_value = models.FloatField()
    unit = models.CharField(max_length=10, default='A')
    min_value = models.FloatField()  # Reference from test config
    max_value = models.FloatField()  # Reference from test config
    passed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.measured_value}{self.unit}"

    class Meta:
        verbose_name = "Current Measurement Result"
        verbose_name_plural = "Current Measurement Results"


class ResistanceMeasurementResult(models.Model):
    """Represents a resistance measurement result"""
    test_result = models.ForeignKey(PcbTestResult, on_delete=models.CASCADE, related_name='resistance_measurements')
    parameter_name = models.CharField(max_length=100)
    measured_value = models.FloatField()
    unit = models.CharField(max_length=10, default='Ω')
    min_value = models.FloatField()  # Reference from test config
    max_value = models.FloatField()  # Reference from test config
    passed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.measured_value}{self.unit}"

    class Meta:
        verbose_name = "Resistance Measurement Result"
        verbose_name_plural = "Resistance Measurement Results"


class FrequencyMeasurementResult(models.Model):
    """Represents a frequency measurement result"""
    test_result = models.ForeignKey(PcbTestResult, on_delete=models.CASCADE, related_name='frequency_measurements')
    parameter_name = models.CharField(max_length=100)
    measured_value = models.FloatField()
    unit = models.CharField(max_length=10, default='Hz')
    min_value = models.FloatField()  # Reference from test config
    max_value = models.FloatField()  # Reference from test config
    passed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.measured_value}{self.unit}"

    class Meta:
        verbose_name = "Frequency Measurement Result"
        verbose_name_plural = "Frequency Measurement Results"


class YesNoQuestionResult(models.Model):
    """Represents a yes/no question result"""
    test_result = models.ForeignKey(PcbTestResult, on_delete=models.CASCADE, related_name='yes_no_questions')
    question_text = models.CharField(max_length=500)
    user_answer = models.BooleanField()  # True for 'Yes', False for 'No'
    required_answer = models.BooleanField()  # True for 'Yes', False for 'No' (reference from test config)
    passed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        answer = "Yes" if self.user_answer else "No"
        required = "Yes" if self.required_answer else "No"
        return f"{self.question_text} (Answer: {answer}, Required: {required})"

    class Meta:
        verbose_name = "Yes/No Question Result"
        verbose_name_plural = "Yes/No Question Results"


class InstructionResult(models.Model):
    """Represents an instruction result (acknowledged by technician)"""
    test_result = models.ForeignKey(PcbTestResult, on_delete=models.CASCADE, related_name='instructions')
    instruction_text = models.TextField()
    acknowledged = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Acknowledged" if self.acknowledged else "Not Acknowledged"
        return f"{self.instruction_text} ({status})"

    class Meta:
        verbose_name = "Instruction Result"
        verbose_name_plural = "Instruction Results"


class QaSignoff(models.Model):
    """Represents QA signoff for a PCB test result"""
    test_result = models.OneToOneField(PcbTestResult, on_delete=models.CASCADE, related_name='qa_signoff')
    qa_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qa_signoffs')
    qa_notes = models.TextField(blank=True, null=True)
    signed_off_at = models.DateTimeField(null=True, blank=True)
    is_signed_off = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QA Signoff for {self.test_result.pcb.serial_number} by {self.qa_user.username}"

    def save(self, *args, **kwargs):
        if self.is_signed_off and not self.signed_off_at:
            self.signed_off_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "QA Signoff"
        verbose_name_plural = "QA Signoffs"
        ordering = ['-signed_off_at']