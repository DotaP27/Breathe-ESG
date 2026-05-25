import csv
import io
import math
from decimal import Decimal
from django.utils.dateparse import parse_date
from tenants.models import TenantConfig
import pdfplumber

# Simple airport coordinates sample (lat, lon)
AIRPORT_COORDS = {
    "DEL": (28.5562, 77.1000),
    "BOM": (19.0896, 72.8656),
    "JFK": (40.6413, -73.7781),
    "LAX": (33.9416, -118.4085),
    "LHR": (51.4700, -0.4543),
}

# LHV / conversion factors (examples)
LHV_LITERS_TO_KWH = {
    "DIESEL": Decimal("9.9"),
    "GASOLINE": Decimal("8.9"),
}

EMISSION_FACTORS = {
    "FLIGHT_KG_PER_KM": Decimal("0.255"),
    "TRAIN_KG_PER_KM": Decimal("0.041"),
    "HOTEL_KG_PER_NIGHT": Decimal("30"),
}


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def parse_csv_text(file_bytes):
    text = extract_upload_text(file_bytes)
    buf = io.StringIO(text)
    reader = csv.DictReader(buf)
    return list(reader)


def extract_upload_text(file_bytes):
    """Return plain text from a text/CSV upload or a PDF upload."""
    if not file_bytes:
        return ""
    head = file_bytes[:5]
    is_pdf = head == b"%PDF-" or file_bytes.lstrip().startswith(b"%PDF-")
    if is_pdf:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
        except Exception:
            # Fall back to byte decode if the PDF is image-based or text extraction fails.
            return file_bytes.decode("utf-8", errors="replace")
    return file_bytes.decode("utf-8", errors="replace")


def detect_source_type(file_bytes, filename=None):
    """Detect ingest source from content or filename."""
    text = extract_upload_text(file_bytes)
    sample = text[:4000].upper()
    filename = (filename or "").upper()

    hits = []

    if any(k in sample for k in ("TRANSPORTMODE", "HOTEL_NIGHTS", "ORIGINCODE", "DESTCODE", "TRIPID")):
        hits.append("TRAVEL")
    if any(k in sample for k in ("READING_KWH", "READING_MWH", "BILLINGPERIODSTART", "BILLINGPERIODEND", "METERID", "ACCOUNTNUMBER")):
        hits.append("UTILITY")
    if any(k in sample for k in ("MENGE", "MEINS", "WERKS", "MATNR", "E1MARAM")):
        hits.append("SAP")

    if len(hits) > 1:
        return "MIXED"
    if len(hits) == 1:
        return hits[0]

    # filename fallback if text is sparse
    if "TRAVEL" in filename:
        return "TRAVEL"
    if "UTILITY" in filename or "BILL" in filename:
        return "UTILITY"
    if "SAP" in filename or "MATERIAL" in filename:
        return "SAP"
    return None


def split_sectioned_text(file_bytes):
    """Split a sectioned PDF/text payload into UTILITY / SAP / TRAVEL blocks."""
    text = extract_upload_text(file_bytes)
    lines = text.splitlines()
    sections = {}
    current = None
    buffer = []

    def flush():
        nonlocal buffer, current
        if current and buffer:
            sections[current] = "\n".join(buffer).strip()
        buffer = []

    for line in lines:
        marker = line.strip().upper()
        if marker in {"UTILITY", "SAP", "TRAVEL"}:
            flush()
            current = marker
            continue
        if current:
            buffer.append(line)

    flush()
    return sections


def parse_sap(file_bytes):
    """Very lightweight SAP flat-file parser.
    Strategy: try CSV parsing first. If headers contain German fields like MENGE/MEINS/WERKS,
    map them to canonical names. Otherwise, fallback to line-segment parsing (split by whitespace).
    Returns list of dict rows.
    """
    rows = []
    try:
        reader_rows = parse_csv_text(file_bytes)
        if reader_rows:
            for r in reader_rows:
                # Normalize keys
                row = {k.strip().upper(): v for k, v in r.items()}
                if any(k in row for k in ("MENGE", "MEINS", "WERKS")):
                    rows.append(row)
                    continue
            if rows:
                return rows
    except Exception:
        pass

    # Fallback: simple line-based parse
    text = file_bytes.decode("utf-8", errors="replace")
    for line in text.splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        # detect segment lines like E1MARAM or E1* fields
        if parts[0].upper().startswith("E1") and len(parts) > 1:
            # crude: pairwise key-value if possible
            kv = {}
            for p in parts[1:]:
                if "=" in p:
                    k, v = p.split("=", 1)
                    kv[k.upper()] = v
            if kv:
                rows.append(kv)
    return rows


def normalize_unit_to_kwh(quantity, unit, tenant=None):
    if quantity is None or unit is None:
        return None
    unit = str(unit).strip().upper()
    q = Decimal(str(quantity))
    if unit in ("KWH", "KW H", "KILOWATT-HOUR"):
        return q
    if unit in ("MWH", "MW H"):
        return q * Decimal("1000")
    if unit in ("L", "LTR", "LITER", "LITRE"):
        # assume diesel if not specified; allow tenant override via TenantConfig
        lhv = LHV_LITERS_TO_KWH.get("DIESEL", Decimal("9.9"))
        try:
            if tenant is not None and hasattr(tenant, 'config'):
                ef = tenant.config.emission_factors or {}
                if ef.get('LHV_LITERS_TO_KWH_DIESEL'):
                    lhv = Decimal(str(ef.get('LHV_LITERS_TO_KWH_DIESEL')))
        except Exception:
            pass
        return q * lhv
    if unit in ("GAL", "GALLON"):
        # convert gallons to liters (approx 3.78541) then to kWh via diesel
        liters = q * Decimal("3.78541")
        return liters * LHV_LITERS_TO_KWH.get("DIESEL", Decimal("9.9"))
    # unknown: return None
    return None


def parse_utility(file_bytes, tenant=None):
    rows = parse_csv_text(file_bytes)
    parsed = []
    for r in rows:
        # normalize keys lower
        rr = {k.strip(): v for k, v in r.items()}
        # attempt to detect reading unit
        reading = None
        unit = "kWh"
        # Prefer a populated kWh field, then a populated MWh field, then any matching suffix.
        if rr.get("Reading_kWh") not in (None, ""):
            reading = rr.get("Reading_kWh")
            unit = "kWh"
        elif rr.get("Reading_MWh") not in (None, ""):
            reading = rr.get("Reading_MWh")
            unit = "MWh"
        else:
            # try other keys
            for key in rr:
                if key.lower().endswith("kwh") and rr.get(key) not in (None, ""):
                    reading = rr[key]
                    unit = "kWh"
                    break
                if key.lower().endswith("mwh") and rr.get(key) not in (None, ""):
                    reading = rr[key]
                    unit = "MWh"
                    break
        try:
            q = Decimal(str(reading)) if reading not in (None, "") else None
        except Exception:
            q = None
        kwh = normalize_unit_to_kwh(q, unit, tenant=tenant) if q is not None else None
        parsed.append({
            "raw": rr,
            "quantity": q,
            "quantity_kwh": kwh,
            "billing_start": rr.get("BillingPeriodStart") or rr.get("StartDate"),
            "billing_end": rr.get("BillingPeriodEnd") or rr.get("EndDate"),
        })
    return parsed


def validate_utility_parsed_row(parsed_row):
    """Return a list of validation error strings for a utility parsed row."""
    errs = []
    # quantity_kwh should be present and positive
    q = parsed_row.get("quantity_kwh")
    if q in (None, ""):
        errs.append("quantity_kwh missing or could not be parsed")
    else:
        try:
            if Decimal(str(q)) <= 0:
                errs.append("quantity_kwh must be positive")
        except Exception:
            errs.append("quantity_kwh is not a valid number")

    # billing dates if present should be parseable
    for dkey in ("billing_start", "billing_end"):
        d = parsed_row.get(dkey)
        if d:
            try:
                if isinstance(d, str):
                    _ = parse_date(d)
                    if _ is None:
                        errs.append(f"{dkey} not parseable as date: {d}")
            except Exception:
                errs.append(f"{dkey} not parseable as date: {d}")

    return errs


def validate_travel_parsed_row(parsed_row):
    errs = []
    mode = (parsed_row.get("mode") or "").upper()
    if not mode:
        errs.append("transport mode missing")

    dk = parsed_row.get("distance_km")
    if dk in (None, ""):
        # allow missing if hotel nights exist (mode HOTEL) else error
        if mode != "HOTEL":
            errs.append("distance_km missing and could not be inferred")
    else:
        try:
            if Decimal(str(dk)) < 0:
                errs.append("distance_km must be non-negative")
        except Exception:
            errs.append("distance_km is not a valid number")

    return errs


def validate_sap_parsed_row(parsed_row):
    errs = []
    # check for quantity fields
    qty = parsed_row.get("MENGE") or parsed_row.get("quantity") or parsed_row.get("AMOUNT")
    if qty in (None, ""):
        errs.append("quantity missing for SAP row")
    else:
        try:
            Decimal(str(qty))
        except Exception:
            errs.append("quantity is not a valid number")
    return errs


def parse_travel(file_bytes, tenant=None):
    rows = parse_csv_text(file_bytes)
    parsed = []
    for r in rows:
        rr = {k.strip(): v for k, v in r.items()}
        mode = (rr.get("TransportMode") or rr.get("Transport_Mode") or "").upper()
        distance = rr.get("Distance_km") or rr.get("Distance")
        distance_km = None
        try:
            distance_km = Decimal(str(distance)) if distance not in (None, "") else None
        except Exception:
            distance_km = None

        # If missing distance and have airport codes, compute haversine
        if not distance_km and rr.get("OriginCode") and rr.get("DestCode"):
            o = rr.get("OriginCode").upper()
            d = rr.get("DestCode").upper()
            if o in AIRPORT_COORDS and d in AIRPORT_COORDS:
                lat1, lon1 = AIRPORT_COORDS[o]
                lat2, lon2 = AIRPORT_COORDS[d]
                km = haversine_km(lat1, lon1, lat2, lon2)
                distance_km = Decimal(str(round(km, 3)))

        co2e = None
        # allow tenant overrides for emission factors
        ef_flight = EMISSION_FACTORS["FLIGHT_KG_PER_KM"]
        ef_train = EMISSION_FACTORS["TRAIN_KG_PER_KM"]
        ef_hotel = EMISSION_FACTORS["HOTEL_KG_PER_NIGHT"]
        try:
            if tenant is not None and hasattr(tenant, 'config'):
                ef = tenant.config.emission_factors or {}
                if ef.get('FLIGHT_KG_PER_KM'):
                    ef_flight = Decimal(str(ef.get('FLIGHT_KG_PER_KM')))
                if ef.get('TRAIN_KG_PER_KM'):
                    ef_train = Decimal(str(ef.get('TRAIN_KG_PER_KM')))
                if ef.get('HOTEL_KG_PER_NIGHT'):
                    ef_hotel = Decimal(str(ef.get('HOTEL_KG_PER_NIGHT')))
        except Exception:
            pass

        if distance_km and mode == "FLIGHT":
            co2e = distance_km * ef_flight
        elif distance_km and mode == "TRAIN":
            co2e = distance_km * ef_train
        elif mode == "HOTEL":
            nights = rr.get("Hotel_Nights") or rr.get("HotelNights") or "0"
            try:
                nights_i = Decimal(str(nights))
            except Exception:
                nights_i = Decimal("0")
            co2e = nights_i * ef_hotel

        parsed.append({
            "raw": rr,
            "mode": mode,
            "distance_km": distance_km,
            "co2e_kg": co2e,
        })
    return parsed
