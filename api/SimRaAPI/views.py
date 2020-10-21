from rest_framework import viewsets
from rest_framework_gis.filters import InBBOXFilter, GeometryFilter, GeoFilterSet

from .models import Incident, Ride, ParsedFiles
from .serializers import IncidentSerializer, RideSerializer, ParsedFilesSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend


import memcache
memcache.SERVER_MAX_VALUE_LENGTH = 1024*1024*100


class ParsedFilesViewSet(viewsets.ModelViewSet):
    queryset = ParsedFiles.objects.all()
    serializer_class = ParsedFilesSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    bbox_filter_field = "geom"
    filter_backends = (InBBOXFilter,)

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, request, *args, **kwargs):
        return super(IncidentViewSet, self).dispatch(request, *args, **kwargs)


class ContainsFilter(GeoFilterSet):
    contains = GeometryFilter(
            field_name = 'geom', lookup_expr='crosses'
    )

    containsStart = GeometryFilter(
            field_name = 'start', lookup_expr='coveredby'
    )
    containsEnd = GeometryFilter(
            field_name = 'end', lookup_expr='coveredby'
    )

    class Meta:
        model = Ride
        fields = ['contains', 'containsStart', 'containsEnd']


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    bbox_filter_field = "geom"

    filter_class = ContainsFilter
    filter_backends = (InBBOXFilter, DjangoFilterBackend)

