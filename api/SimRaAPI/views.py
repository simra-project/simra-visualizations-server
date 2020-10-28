from rest_framework import viewsets
from rest_framework_gis.filters import InBBOXFilter, GeometryFilter, GeoFilterSet

from .models import Incident, Ride, ParsedFiles, OsmWaysLegs
from .serializers import IncidentSerializer, RideSerializer, ParsedFilesSerializer, LegSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from django.db import connection
from django.http import HttpResponse

import memcache

memcache.SERVER_MAX_VALUE_LENGTH = 1024 * 1024 * 100


class ParsedFilesViewSet(viewsets.ModelViewSet):
    queryset = ParsedFiles.objects.all()
    serializer_class = ParsedFilesSerializer


class IncidentContainsFilter(GeoFilterSet):
    contains = GeometryFilter(
        field_name='geom', lookup_expr='coveredby'
    )

    class Meta:
        model = Incident
        fields = ['contains']


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    bbox_filter_field = "geom"

    filter_class = IncidentContainsFilter
    filter_backends = (InBBOXFilter, DjangoFilterBackend)

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, request, *args, **kwargs):
        return super(IncidentViewSet, self).dispatch(request, *args, **kwargs)


class ContainsFilter(GeoFilterSet):
    contains = GeometryFilter(
        field_name='geom', lookup_expr='crosses'
    )

    containsStart = GeometryFilter(
        field_name='start', lookup_expr='coveredby'
    )
    containsEnd = GeometryFilter(
        field_name='end', lookup_expr='coveredby'
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


class LegViewSet(viewsets.ModelViewSet):
    queryset = OsmWaysLegs.objects.all()
    serializer_class = LegSerializer
    bbox_filter_field = "geom"
    filter_backends = (InBBOXFilter,)


def get_statistics(request, region):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
               r_count,
               r_meters,
               r_seconds,
               (r_meters * 0.183) / 1000 as r_savedco2,
               r_meters/r_count as r_avg_distance,
               r_seconds/r_count as r_avg_duration,
               r_meters/r_seconds as r_avg_velocity,
               i_count,
               i_count_scary,
               i_count_child,
               i_count_trailer,
               i_incident_minus_1,
               i_incident_0,
               i_incident_1,
               i_incident_2,
               i_incident_3,
               i_incident_4,
               i_incident_5,
               i_incident_6,
               i_incident_7,
               i_incident_8,
               i_iType_minus_1,
               i_iType_0,
               i_iType_1,
               i_iType_2,
               i_iType_3,
               i_iType_4,
               i_iType_5,
               i_iType_6,
               i_iType_7,
               i_iType_8,
               i_iType_9,
               i_iType_10
        FROM (
            SELECT
               COUNT(*) as r_count,
               Sum(ST_Length(geom::geography)) as r_meters,
               EXTRACT(EPOCH FROM (SUM(timestamps[array_upper(timestamps, 1)] - timestamps[1]))) as r_seconds
            FROM "SimRaAPI_ride" INNER JOIN "SimRaAPI_parsedfiles" SRAp on "SimRaAPI_ride".filename = SRAp."fileName"
            WHERE region = %s
        ) r , (
            SELECT
                COUNT(*) as i_count,
                sum(CASE WHEN scary THEN 1 ELSE 0 END) as i_count_scary,
                sum(CASE WHEN "childCheckbox" THEN 1 ELSE 0 END) as i_count_child,
                sum(CASE WHEN "trailerCheckbox" THEN 1 ELSE 0 END) as i_count_trailer,
                COUNT(incident) filter (where incident = -1) as i_incident_minus_1,
                COUNT(incident) filter (where incident = 0) as i_incident_0,
                COUNT(incident) filter (where incident = 1) as i_incident_1,
                COUNT(incident) filter (where incident = 2) as i_incident_2,
                COUNT(incident) filter (where incident = 3) as i_incident_3,
                COUNT(incident) filter (where incident = 4) as i_incident_4,
                COUNT(incident) filter (where incident = 5) as i_incident_5,
                COUNT(incident) filter (where incident = 6) as i_incident_6,
                COUNT(incident) filter (where incident = 7) as i_incident_7,
                COUNT(incident) filter (where incident = 8) as i_incident_8,
                COUNT("iType") filter (where "iType" = -1) as i_iType_minus_1,
                COUNT("iType") filter (where "iType" = 0) as i_iType_0,
                COUNT("iType") filter (where "iType" = 1) as i_iType_1,
                COUNT("iType") filter (where "iType" = 2) as i_iType_2,
                COUNT("iType") filter (where "iType" = 3) as i_iType_3,
                COUNT("iType") filter (where "iType" = 4) as i_iType_4,
                COUNT("iType") filter (where "iType" = 5) as i_iType_5,
                COUNT("iType") filter (where "iType" = 6) as i_iType_6,
                COUNT("iType") filter (where "iType" = 7) as i_iType_7,
                COUNT("iType") filter (where "iType" = 8) as i_iType_8,
                COUNT("iType") filter (where "iType" = 9) as i_iType_9,
                COUNT("iType") filter (where "iType" = 10) as i_iType_10
            FROM "SimRaAPI_incident" INNER JOIN "SimRaAPI_parsedfiles" SRAp on "SimRaAPI_incident".filename = SRAp."fileName"
            WHERE region = %s) i
                ''', [region, region])
        columns = [col[0] for col in cursor.description]
        return HttpResponse([dict(zip(columns, row)) for row in cursor.fetchall()])
