from django.contrib import admin
from .models import EmissionRecord, IngestionBatch


@admin.register(IngestionBatch)
class IngestionBatchAdmin(admin.ModelAdmin):
	list_display = ("filename", "source_type", "tenant", "uploaded_by", "uploaded_at")


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
	list_display = ("id", "tenant", "source_type", "scope", "status", "created_at")
	list_filter = ("status", "source_type", "scope")
	search_fields = ("id",)
