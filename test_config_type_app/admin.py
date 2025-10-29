from django.contrib import admin
from .models import TestConfigType, VoltageMeasurement, CurrentMeasurement, YesNoQuestion, ResistanceMeasurement, FrequencyMeasurement


class VoltageMeasurementInline(admin.TabularInline):
    model = VoltageMeasurement
    extra = 1


class CurrentMeasurementInline(admin.TabularInline):
    model = CurrentMeasurement
    extra = 1


class YesNoQuestionInline(admin.TabularInline):
    model = YesNoQuestion
    extra = 1


class ResistanceMeasurementInline(admin.TabularInline):
    model = ResistanceMeasurement
    extra = 1


class FrequencyMeasurementInline(admin.TabularInline):
    model = FrequencyMeasurement
    extra = 1


@admin.register(TestConfigType)
class TestConfigTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [
        VoltageMeasurementInline,
        CurrentMeasurementInline,
        YesNoQuestionInline,
        ResistanceMeasurementInline,
        FrequencyMeasurementInline,
    ]


@admin.register(VoltageMeasurement)
class VoltageMeasurementAdmin(admin.ModelAdmin):
    list_display = ['parameter_name', 'min_value', 'max_value', 'unit', 'test_config']
    list_filter = ['test_config']
    search_fields = ['parameter_name', 'test_config__name']


@admin.register(CurrentMeasurement)
class CurrentMeasurementAdmin(admin.ModelAdmin):
    list_display = ['parameter_name', 'min_value', 'max_value', 'unit', 'test_config']
    list_filter = ['test_config']
    search_fields = ['parameter_name', 'test_config__name']


@admin.register(YesNoQuestion)
class YesNoQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'required_answer', 'test_config']
    list_filter = ['test_config', 'required_answer']
    search_fields = ['question_text', 'test_config__name']


@admin.register(ResistanceMeasurement)
class ResistanceMeasurementAdmin(admin.ModelAdmin):
    list_display = ['parameter_name', 'min_value', 'max_value', 'unit', 'test_config']
    list_filter = ['test_config']
    search_fields = ['parameter_name', 'test_config__name']


@admin.register(FrequencyMeasurement)
class FrequencyMeasurementAdmin(admin.ModelAdmin):
    list_display = ['parameter_name', 'min_value', 'max_value', 'unit', 'test_config']
    list_filter = ['test_config']
    search_fields = ['parameter_name', 'test_config__name']