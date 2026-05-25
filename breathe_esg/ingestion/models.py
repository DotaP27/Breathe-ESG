from django.db import models


# Placeholder models for ingestion app. Parsing logic will live here.
class ParsedRow(models.Model):
    raw_line = models.TextField()
    parsed_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)
