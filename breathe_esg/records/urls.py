from django.urls import path
from .views import PendingRecordsListAPIView, ApproveRecordAPIView, FlagRecordAPIView, RejectRecordAPIView, AuditRecordsListAPIView, AuditExportAPIView

urlpatterns = [
    path("pending/", PendingRecordsListAPIView.as_view(), name="records-pending"),
    path("audit/", AuditRecordsListAPIView.as_view(), name="records-audit"),
    path("audit/export/", AuditExportAPIView.as_view(), name="records-audit-export"),
    path("<int:pk>/approve/", ApproveRecordAPIView.as_view(), name="record-approve"),
    path("<int:pk>/flag/", FlagRecordAPIView.as_view(), name="record-flag"),
    path("<int:pk>/reject/", RejectRecordAPIView.as_view(), name="record-reject"),
]
