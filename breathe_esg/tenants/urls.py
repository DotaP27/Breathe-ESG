from django.urls import path
from .views import TenantConfigAPIView, TenantsListAPIView

urlpatterns = [
    path('', TenantsListAPIView.as_view(), name='tenants-list'),
    path('<int:tenant_id>/config/', TenantConfigAPIView.as_view(), name='tenant-config'),
]
