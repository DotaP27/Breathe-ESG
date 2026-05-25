from rest_framework import serializers
from .models import EmissionRecord


class EmissionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionRecord
        fields = [
            "id",
            "tenant",
            "source_type",
            "source_file",
            "raw_data",
            "scope",
            "quantity_kwh",
            "co2e_kg",
            "fuel_type",
            "measurement_unit",
            "status",
            "reviewed_by",
            "reviewed_at",
            "edit_history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("edit_history", "created_at", "updated_at", "reviewed_by", "reviewed_at")
