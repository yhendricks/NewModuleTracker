from django.contrib import admin
from .models import ModuleConfigType, ModuleConfigPcb

class ModuleConfigPcbInline(admin.TabularInline):
    model = ModuleConfigPcb
    extra = 1 # Number of empty forms to display

@admin.register(ModuleConfigType)
class ModuleConfigTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ModuleConfigPcbInline]
