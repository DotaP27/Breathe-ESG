from django.contrib import admin
from .models import Tenant, TenantConfig, Plant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug')


@admin.register(TenantConfig)
class TenantConfigAdmin(admin.ModelAdmin):
    list_display = ('tenant',)
    readonly_fields = ()


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'code', 'name', 'country')
    list_filter = ('tenant', 'country')
    search_fields = ('code', 'name')
