from django.contrib import admin
from .models import Module, ATPReport, ESSReport

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_config', 'status')
    list_filter = ('status', 'module_config')
    search_fields = ('name',)

@admin.register(ATPReport)
class ATPReportAdmin(admin.ModelAdmin):
    list_display = ('module', 'test_phase', 'qa_signoff', 'signed_off_by', 'timestamp')
    list_filter = ('test_phase', 'qa_signoff')
    search_fields = ('module__name',)

@admin.register(ESSReport)
class ESSReportAdmin(admin.ModelAdmin):
    list_display = ('module', 'qa_signoff', 'signed_off_by', 'timestamp')
    list_filter = ('qa_signoff',)
    search_fields = ('module__name',)
