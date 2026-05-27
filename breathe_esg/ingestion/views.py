from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

import hashlib
from records.models import IngestionBatch, EmissionRecord
from tenants.models import Tenant
from .parsers import (
    parse_sap,
    parse_utility,
    parse_travel,
    detect_source_type,
    split_sectioned_text,
    validate_utility_parsed_row,
    validate_travel_parsed_row,
    validate_sap_parsed_row,
)

class IngestFileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        f = request.FILES.get("file")
        tenant_id = request.data.get("tenant_id") or 1
        if not f:
            return Response({"error": "file and tenant_id required"}, status=status.HTTP_400_BAD_REQUEST)
        tenant, _ = Tenant.objects.get_or_create(
            pk=tenant_id,
            defaults={"name": "Default Tenant", "slug": "default-tenant"},
        )
        content = f.read()
        # compute sha256 fingerprint for dedup detection
        file_hash = hashlib.sha256(content).hexdigest()
        source_type = detect_source_type(content, filename=f.name)
        if not source_type:
            return Response({"error": "unable to detect source type from file"}, status=status.HTTP_400_BAD_REQUEST)

        # duplicate file prevention: same tenant and same hash
        if IngestionBatch.objects.filter(tenant=tenant, file_hash=file_hash).exists():
            return Response({"error": "duplicate upload detected (same file already ingested)"}, status=status.HTTP_409_CONFLICT)

        batch = IngestionBatch.objects.create(
            tenant=tenant,
            filename=f.name,
            file_hash=file_hash,
            source_type=source_type.upper(),
            uploaded_by=request.user,
            metadata={"size": f.size}
        )

        parsed = []
        created = []
        errors = []
        try:
            if source_type.upper() == "SAP":
                parsed = parse_sap(content)
                for r in parsed:
                    # map likely fields
                    qty = r.get("MENGE") or r.get("quantity") or r.get("AMOUNT")
                    unit = r.get("MEINS") or r.get("unit")
                    try:
                        quantity = float(qty) if qty not in (None, "") else None
                    except Exception:
                        quantity = None
                    quantity_kwh = None
                    if quantity is not None:
                        quantity_kwh = None
                    errs = validate_sap_parsed_row(r)
                    rec = EmissionRecord(
                        tenant=tenant,
                        source_type="SAP",
                        source_file=batch,
                        raw_data=r,
                        scope=1,
                        quantity_kwh=quantity_kwh,
                    )
                    if errs:
                        # attach errors to raw_data for audit
                        try:
                            rec.raw_data["_errors"] = errs
                        except Exception:
                            pass
                    created.append(rec)
            elif source_type.upper() == "UTILITY":
                parsed = parse_utility(content, tenant=tenant)
                for r in parsed:
                    errs = validate_utility_parsed_row(r)
                    rec = EmissionRecord(
                        tenant=tenant,
                        source_type="UTILITY",
                        source_file=batch,
                        raw_data=r["raw"],
                        scope=2,
                        quantity_kwh=r.get("quantity_kwh"),
                    )
                    if errs:
                        try:
                            rec.raw_data["_errors"] = errs
                        except Exception:
                            pass
                    created.append(rec)
            elif source_type.upper() == "TRAVEL":
                parsed = parse_travel(content, tenant=tenant)
                for r in parsed:
                    errs = validate_travel_parsed_row(r)
                    rec = EmissionRecord(
                        tenant=tenant,
                        source_type="TRAVEL",
                        source_file=batch,
                        raw_data=r.get("raw"),
                        scope=3,
                        quantity_kwh=None,
                        co2e_kg=r.get("co2e_kg"),
                    )
                    if errs:
                        try:
                            rec.raw_data["_errors"] = errs
                        except Exception:
                            pass
                    created.append(rec)
            elif source_type.upper() == "MIXED":
                sections = split_sectioned_text(content)
                if sections.get("UTILITY"):
                    utility_rows = parse_utility(sections["UTILITY"].encode("utf-8"), tenant=tenant)
                    for r in utility_rows:
                        errs = validate_utility_parsed_row(r)
                        rec = EmissionRecord(
                            tenant=tenant,
                            source_type="UTILITY",
                            source_file=batch,
                            raw_data=r["raw"],
                            scope=2,
                            quantity_kwh=r.get("quantity_kwh"),
                        )
                        if errs:
                            try:
                                rec.raw_data["_errors"] = errs
                            except Exception:
                                pass
                        created.append(rec)
                    parsed.extend(utility_rows)
                if sections.get("SAP"):
                    sap_rows = parse_sap(sections["SAP"].encode("utf-8"))
                    for r in sap_rows:
                        qty = r.get("MENGE") or r.get("quantity") or r.get("AMOUNT")
                        try:
                            quantity = float(qty) if qty not in (None, "") else None
                        except Exception:
                            quantity = None
                        errs = validate_sap_parsed_row(r)
                        rec = EmissionRecord(
                            tenant=tenant,
                            source_type="SAP",
                            source_file=batch,
                            raw_data=r,
                            scope=1,
                            quantity_kwh=None if quantity is not None else None,
                        )
                        if errs:
                            try:
                                rec.raw_data["_errors"] = errs
                            except Exception:
                                pass
                        created.append(rec)
                    parsed.extend(sap_rows)
                if sections.get("TRAVEL"):
                    travel_rows = parse_travel(sections["TRAVEL"].encode("utf-8"), tenant=tenant)
                    for r in travel_rows:
                        errs = validate_travel_parsed_row(r)
                        rec = EmissionRecord(
                            tenant=tenant,
                            source_type="TRAVEL",
                            source_file=batch,
                            raw_data=r.get("raw"),
                            scope=3,
                            quantity_kwh=None,
                            co2e_kg=r.get("co2e_kg"),
                        )
                        if errs:
                            try:
                                rec.raw_data["_errors"] = errs
                            except Exception:
                                pass
                        created.append(rec)
                    parsed.extend(travel_rows)
            else:
                return Response({"error": "unknown source_type"}, status=status.HTTP_400_BAD_REQUEST)

            if created:
                EmissionRecord.objects.bulk_create(created)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"batch_id": batch.id, "source_type": source_type.upper(), "parsed_rows": len(parsed), "created": len(created), "errors": errors})
