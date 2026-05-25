from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import WhoAmIAPIView
from .views import RegisterAPIView

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("ingestion/", include("ingestion.urls")),
    path("records/", include("records.urls")),
    path("tenants/", include("tenants.urls")),
    path("me/", WhoAmIAPIView.as_view(), name='whoami'),
]
