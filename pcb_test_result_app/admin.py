from django.contrib import admin
from .models import (
    PcbTestResult, 
    VoltageMeasurementResult, 
    CurrentMeasurementResult, 
    ResistanceMeasurementResult, 
    FrequencyMeasurementResult, 
    YesNoQuestionResult, 
    InstructionResult
)

@admin.register(PcbTestResult)
class PcbTestResultAdmin(admin.ModelAdmin):
    list_display = ('pcb', 'technician', 'result', 'test_date', 'created_at')
    list_filter = ('result', 'test_date', 'technician')
    search_fields = ('pcb__serial_number', 'technician__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(VoltageMeasurementResult)
class VoltageMeasurementResultAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'parameter_name', 'measured_value', 'unit', 'passed', 'created_at')
    list_filter = ('passed', 'created_at')
    search_fields = ('parameter_name', 'test_result__pcb__serial_number')
    readonly_fields = ('created_at',)

@admin.register(CurrentMeasurementResult)
class CurrentMeasurementResultAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'parameter_name', 'measured_value', 'unit', 'passed', 'created_at')
    list_filter = ('passed', 'created_at')
    search_fields = ('parameter_name', 'test_result__pcb__serial_number')
    readonly_fields = ('created_at',)

@admin.register(ResistanceMeasurementResult)
class ResistanceMeasurementResultAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'parameter_name', 'measured_value', 'unit', 'passed', 'created_at')
    list_filter = ('passed', 'created_at')
    search_fields = ('parameter_name', 'test_result__pcb__serial_number')
    readonly_fields = ('created_at',)

@admin.register(FrequencyMeasurementResult)
class FrequencyMeasurementResultAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'parameter_name', 'measured_value', 'unit', 'passed', 'created_at')
    list_filter = ('passed', 'created_at')
    search_fields = ('parameter_name', 'test_result__pcb__serial_number')
    readonly_fields = ('created_at',)

@admin.register(YesNoQuestionResult)
class YesNoQuestionResultAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'question_text', 'user_answer', 'required_answer', 'passed', 'created_at')
    list_filter = ('passed', 'created_at', 'user_answer')
    search_fields = ('question_text', 'test_result__pcb__serial_number')
    readonly_fields = ('created_at',)

@admin.register(InstructionResult)
class InstructionResultAdmin(admin.ModelAdmin):
    list_display = ('test_result', 'instruction_text', 'acknowledged', 'created_at')
    list_filter = ('acknowledged', 'created_at')
    search_fields = ('instruction_text', 'test_result__pcb__serial_number')
    readonly_fields = ('created_at',)
