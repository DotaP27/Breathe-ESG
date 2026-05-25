from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Tenant, TenantConfig
from .serializers import TenantConfigSerializer
from .serializers import TenantSerializer


class TenantsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # admin-only
        if not request.user.is_staff:
            return Response({'detail': 'staff only'}, status=status.HTTP_403_FORBIDDEN)
        tenants = Tenant.objects.all()
        ser = TenantSerializer(tenants, many=True)
        return Response(ser.data)


class TenantConfigAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        config, _ = TenantConfig.objects.get_or_create(tenant=tenant)
        ser = TenantConfigSerializer(config)
        return Response(ser.data)

    def put(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        config, _ = TenantConfig.objects.get_or_create(tenant=tenant)
        ser = TenantConfigSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.update(config, ser.validated_data)
        return Response(TenantConfigSerializer(config).data)
