from django.test import TestCase
from tenants.models import Tenant, TenantConfig
from ingestion.parsers import parse_utility, parse_travel, parse_sap, detect_source_type, extract_upload_text
from decimal import Decimal


class ParserTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Demo', slug='demo')
        TenantConfig.objects.create(tenant=self.tenant, emission_factors={
            'FLIGHT_KG_PER_KM': 0.25,
            'HOTEL_KG_PER_NIGHT': 28,
            'LHV_LITERS_TO_KWH_DIESEL': 9.8,
        })

    def test_parse_utility_basic(self):
        import os
        here = os.path.dirname(__file__)
        samples_dir = os.path.abspath(os.path.join(here, '..', 'samples'))
        data = open(os.path.join(samples_dir, 'sample_utility.csv'),'rb').read()
        parsed = parse_utility(data, tenant=self.tenant)
        self.assertEqual(len(parsed), 2)
        self.assertIsNotNone(parsed[0]['quantity_kwh'])
        self.assertEqual(parsed[0]['quantity_kwh'], Decimal('4821.5'))

    def test_parse_travel_haversine_and_factors(self):
        import os
        here = os.path.dirname(__file__)
        samples_dir = os.path.abspath(os.path.join(here, '..', 'samples'))
        data = open(os.path.join(samples_dir, 'sample_travel.csv'),'rb').read()
        parsed = parse_travel(data, tenant=self.tenant)
        # first row DEL->BOM should compute distance and co2e
        self.assertTrue(len(parsed) >= 2)
        first = parsed[0]
        self.assertEqual(first['mode'], 'FLIGHT')
        self.assertIsNotNone(first['distance_km'])
        self.assertIsNotNone(first['co2e_kg'])

    def test_parse_sap_fallback(self):
        import os
        here = os.path.dirname(__file__)
        samples_dir = os.path.abspath(os.path.join(here, '..', 'samples'))
        data = open(os.path.join(samples_dir, 'sample_sap.txt'),'rb').read()
        parsed = parse_sap(data)
        self.assertTrue(len(parsed) >= 1)
        self.assertIn('MENGE', parsed[0])

    def test_detect_source_type_and_parse_pdf_utility(self):
        import os
        here = os.path.dirname(__file__)
        samples_dir = os.path.abspath(os.path.join(here, '..', 'samples'))
        data = open(os.path.join(samples_dir, 'sample_utility_pdf.pdf'), 'rb').read()
        self.assertEqual(detect_source_type(data, filename='sample_utility_pdf.pdf'), 'UTILITY')
        text = extract_upload_text(data)
        self.assertIn('ACC-PDF-1', text)
        parsed = parse_utility(data, tenant=self.tenant)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['quantity_kwh'], Decimal('312.75'))
