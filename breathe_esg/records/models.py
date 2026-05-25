from django.db import models
from django.conf import settings


class IngestionBatch(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)
    filename = models.CharField(max_length=512)
    file_hash = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    source_type = models.CharField(max_length=32)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.filename} ({self.source_type})"


class EmissionRecord(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)

    SOURCE_CHOICES = [("SAP", "SAP"), ("UTILITY", "UTILITY"), ("TRAVEL", "TRAVEL")]
    source_type = models.CharField(max_length=16, choices=SOURCE_CHOICES)
    source_file = models.ForeignKey(IngestionBatch, null=True, on_delete=models.SET_NULL)
    raw_data = models.JSONField()

    SCOPE_CHOICES = [(1, "Scope 1"), (2, "Scope 2"), (3, "Scope 3")]
    scope = models.IntegerField(choices=SCOPE_CHOICES)

    quantity_kwh = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    co2e_kg = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)

    fuel_type = models.CharField(max_length=64, blank=True, null=True)
    measurement_unit = models.CharField(max_length=32, blank=True, null=True)

    STATUS_CHOICES = [("PENDING", "Pending"), ("APPROVED", "Approved"), ("FLAGGED", "Flagged"), ("LOCKED", "Locked"), ("ERROR", "Error")]
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PENDING")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_records"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    edit_history = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["source_type"]),
        ]

    def __str__(self):
        return f"EmissionRecord {self.id} ({self.source_type})"
