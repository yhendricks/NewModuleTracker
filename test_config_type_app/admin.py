from django.contrib import admin
from .models import TestConfigType, TestStep


class TestStepInline(admin.TabularInline):
    model = TestStep
    extra = 1
    fields = ['order', 'step_type', 'parameter_name', 'min_value', 'max_value', 'unit', 'question_text', 'required_answer', 'instruction_text']
    ordering = ['order']


@admin.register(TestConfigType)
class TestConfigTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TestStepInline]


@admin.register(TestStep)
class TestStepAdmin(admin.ModelAdmin):
    list_display = ['test_config', 'order', 'step_type', 'parameter_name', 'question_text', 'instruction_text']
    list_filter = ['step_type', 'test_config']
    search_fields = ['test_config__name', 'parameter_name', 'question_text', 'instruction_text']
    ordering = ['test_config', 'order']