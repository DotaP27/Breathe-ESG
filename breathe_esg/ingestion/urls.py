from django.urls import path
from .views import IngestFileAPIView

urlpatterns = [
    path("upload/", IngestFileAPIView.as_view(), name="ingest-upload"),
]
