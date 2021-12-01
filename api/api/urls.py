"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path, include, path
from rest_framework import routers
from SimRaAPI.views import (
    RideViewSet,
    IncidentViewSet,
    ParsedFilesViewSet,
    LegViewSet,
    get_statistics,
    get_regions,
)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"rides", RideViewSet)
router.register(r"incidents", IncidentViewSet)
router.register(r"files", ParsedFilesViewSet)
router.register(r"legs", LegViewSet)

urlpatterns = [
    re_path(r"^api/", include(router.urls)),
    path(
        "api/statistics/<str:region>/", get_statistics
    ),  # get statistics for a specific region
    path("api/regions/", get_regions),  # get all regions as list
]
