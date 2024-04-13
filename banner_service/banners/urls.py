from django.urls import path
from .views import *

urlpatterns = [
    path('user_banner/', UserBannerView.as_view(), name='user_banner'),
    path('banner/', BannerView.as_view(), name='banner_info'),
    path('banner/<int:id>/<uuid:uuid>/', BannerIdVersionView.as_view(), name='banner_version_operations'),
    path('banner/<int:id>/', BannerIdView.as_view(), name='banner_id_operations'),
]
