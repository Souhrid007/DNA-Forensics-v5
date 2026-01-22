from django.contrib import admin
from .models import Case, Sample


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'title', 'status', 'created_at')
    search_fields = ('case_id', 'title')
    list_filter = ('status', 'created_at')


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'case', 'status', 'uploaded_at')
    search_fields = ('sample_id', 'case__case_id', 'fingerprint_id')
    list_filter = ('status', 'uploaded_at')
