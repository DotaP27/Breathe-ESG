from rest_framework import serializers
from .models import TenantConfig


class TenantConfigSerializer(serializers.Serializer):
    FLIGHT_KG_PER_KM = serializers.DecimalField(max_digits=10, decimal_places=6, required=False)
    TRAIN_KG_PER_KM = serializers.DecimalField(max_digits=10, decimal_places=6, required=False)
    HOTEL_KG_PER_NIGHT = serializers.DecimalField(max_digits=10, decimal_places=6, required=False)
    LHV_LITERS_TO_KWH_DIESEL = serializers.DecimalField(max_digits=10, decimal_places=6, required=False)

    def to_representation(self, instance: TenantConfig):
        ef = instance.emission_factors or {}
        return {
            'FLIGHT_KG_PER_KM': ef.get('FLIGHT_KG_PER_KM'),
            'TRAIN_KG_PER_KM': ef.get('TRAIN_KG_PER_KM'),
            'HOTEL_KG_PER_NIGHT': ef.get('HOTEL_KG_PER_NIGHT'),
            'LHV_LITERS_TO_KWH_DIESEL': ef.get('LHV_LITERS_TO_KWH_DIESEL'),
        }

    def update(self, instance: TenantConfig, validated_data):
        ef = instance.emission_factors or {}
        for k, v in validated_data.items():
            ef[k] = float(v)
        instance.emission_factors = ef
        instance.save()
        return instance

    def create(self, validated_data):
        # Not used
        return TenantConfig.objects.create(emission_factors=validated_data)


from django.contrib.auth import get_user_model
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ('id', 'name', 'slug')
