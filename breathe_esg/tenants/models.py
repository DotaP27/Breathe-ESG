from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TenantConfig(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='config')
    # emission_factors is a JSON blob like {"FLIGHT_KG_PER_KM": 0.255, "HOTEL_KG_PER_NIGHT": 30}
    emission_factors = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Config for {self.tenant.name}"


class Plant(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='plants')
    code = models.CharField(max_length=64)
    name = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=64, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        unique_together = (('tenant', 'code'),)

    def __str__(self):
        return f"{self.tenant.slug}:{self.code}"
