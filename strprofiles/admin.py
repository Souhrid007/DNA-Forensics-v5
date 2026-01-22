from django.contrib import admin
from .models import STRProfile


@admin.register(STRProfile)
class STRProfileAdmin(admin.ModelAdmin):
    list_display = ('sample', 'created_at')
    search_fields = ('sample__sample_id', 'sample__case__case_id')
    readonly_fields = ('created_at',)
