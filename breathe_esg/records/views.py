from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import Group

from .models import EmissionRecord
from .serializers import EmissionRecordSerializer
import csv
from django.http import HttpResponse
import json


class PendingRecordsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmissionRecordSerializer

    def get_queryset(self):
        qs = EmissionRecord.objects.filter(status="PENDING")
        tenant_id = self.request.query_params.get("tenant_id")
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        return qs.order_by("created_at")


class ApproveRecordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, format=None):
        record = get_object_or_404(EmissionRecord, pk=pk)
        if record.status != "PENDING":
            return Response({"error": "Only PENDING records can be approved"}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            # append to edit_history
            history = record.edit_history or []
            history.append({
                "action": "APPROVED",
                "by": request.user.id,
                "ts": timezone.now().isoformat(),
            })
            record.status = "APPROVED"
            record.reviewed_by = request.user
            record.reviewed_at = timezone.now()
            record.edit_history = history
            record.save()
        return Response({"status": "approved", "id": record.id})


def _is_analyst(user):
    if user.is_staff:
        return True
    return user.groups.filter(name="analyst").exists()


class FlagRecordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, format=None):
        # Allow any authenticated user to flag a record for re-review; record will be visible in the audit view
        record = get_object_or_404(EmissionRecord, pk=pk)
        reason = request.data.get("reason") or ""
        with transaction.atomic():
            history = record.edit_history or []
            history.append({
                "action": "FLAGGED",
                "by": request.user.id,
                "ts": timezone.now().isoformat(),
                "reason": reason,
            })
            record.status = "FLAGGED"
            record.reviewed_by = request.user
            record.reviewed_at = timezone.now()
            record.edit_history = history
            record.save()
        return Response({"status": "flagged", "id": record.id})


class RejectRecordAPIView(APIView):
    # Allow any authenticated user to reject a bad record; it will be marked REJECTED
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, format=None):
        record = get_object_or_404(EmissionRecord, pk=pk)
        reason = request.data.get("reason") or ""
        with transaction.atomic():
            history = record.edit_history or []
            history.append({
                "action": "REJECTED",
                "by": request.user.id,
                "ts": timezone.now().isoformat(),
                "reason": reason,
            })
            record.status = "REJECTED"
            record.reviewed_by = request.user
            record.reviewed_at = timezone.now()
            record.edit_history = history
            record.save()
        return Response({"status": "rejected", "id": record.id})


class AuditRecordsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmissionRecordSerializer

    def get_queryset(self):
        # Return approved, locked, or flagged records for a tenant (so flagged items are visible in audit to review again)
        qs = EmissionRecord.objects.filter(status__in=("APPROVED", "LOCKED", "FLAGGED"))
        tenant_id = self.request.query_params.get("tenant_id")
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        return qs.order_by("-reviewed_at")


class AuditExportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        tenant_id = request.query_params.get('tenant_id')
        qs = EmissionRecord.objects.filter(status__in=("APPROVED", "LOCKED", "FLAGGED"))
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        qs = qs.order_by('-reviewed_at')

        # Collect all top-level raw_data keys to flatten into columns
        raw_keys = set()
        for r in qs:
            if isinstance(r.raw_data, dict):
                raw_keys.update(r.raw_data.keys())

        raw_keys = sorted(raw_keys)

        # Prepare CSV
        response = HttpResponse(content_type='text/csv')
        filename = f"audit_tenant_{tenant_id or 'all'}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)

        # Human-friendly headers
        headers = ["ID","Tenant","Source","Source File/Ref","Quantity (kWh)","CO2e (kg)","Status","Reviewed By","Reviewed At","Created At"]
        headers += raw_keys
        writer.writerow(headers)

        for r in qs:
            reviewed_by = r.reviewed_by.username if r.reviewed_by else ''
            # format numbers with 3 decimals where present
            q_kwh = f"{float(r.quantity_kwh):.3f}" if r.quantity_kwh is not None and str(r.quantity_kwh)!='' else ''
            co2 = f"{float(r.co2e_kg):.3f}" if r.co2e_kg is not None and str(r.co2e_kg)!='' else ''
            reviewed_at = r.reviewed_at.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S") if r.reviewed_at else ''
            created_at = r.created_at.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ''

            base_row = [r.id, r.tenant_id, r.source_type, r.source_file or '', q_kwh, co2, r.status, reviewed_by, reviewed_at, created_at]

            # add flattened raw_data values in the same raw_keys order
            rd = r.raw_data or {}
            extra = []
            for k in raw_keys:
                v = rd.get(k, '')
                if isinstance(v, (dict, list)):
                    extra.append(json.dumps(v, ensure_ascii=False))
                else:
                    extra.append(str(v) if v is not None else '')

            writer.writerow(base_row + extra)
        return response
