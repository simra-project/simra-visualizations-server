from rest_framework import viewsets
from rest_framework_gis.filters import InBBOXFilter

from .models import Incident, Ride, ParsedFiles
from .serializers import IncidentSerializer, RideSerializer, ParsedFilesSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

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


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    filter_backends = (InBBOXFilter,)

