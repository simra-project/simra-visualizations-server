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
import json

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

    def get_queryset(self):
        queryset = self.queryset
        ride_id = self.request.GET.get('ride_id')
        exclude_type = self.request.GET.get('exclude_type')
        if ride_id:
            queryset = queryset.filter(ride_id=ride_id)
        if exclude_type:
            queryset = queryset.exclude(incident=exclude_type)
        return queryset

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
               i_iType_10,
               i_bikeType_0,
               i_bikeType_1,
               i_bikeType_2,
               i_bikeType_0,
               i_bikeType_3,
               i_bikeType_4,
               i_bikeType_5,
               i_bikeType_6,
               i_bikeType_7,
               i_bikeType_8,
               p_count,
               p_gender_male,
               p_gender_female,
               p_gender_other,
               p_birth_1_male,
               p_birth_1_female,
               p_birth_1_other,
               p_birth_2_male,
               p_birth_2_female,
               p_birth_2_other,
               p_birth_3_male,
               p_birth_3_female,
               p_birth_3_other,
               p_birth_4_male,
               p_birth_4_female,
               p_birth_4_other,
               p_birth_5_male,
               p_birth_5_female,
               p_birth_5_other,
               p_birth_6_male,
               p_birth_6_female,
               p_birth_6_other,
               p_birth_7_male,
               p_birth_7_female,
               p_birth_7_other,
               p_birth_8_male,
               p_birth_8_female,
               p_birth_8_other,
               p_birth_9_male,
               p_birth_9_female,
               p_birth_9_other,
               p_birth_10_male,
               p_birth_10_female,
               p_birth_10_other,
               p_birth_11_male,
               p_birth_11_female,
               p_birth_11_other,
               p_birth_12_male,
               p_birth_12_female,
               p_birth_12_other,
               p_birth_13_male,
               p_birth_13_female,
               p_birth_13_other
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
                COUNT("iType") filter (where "iType" = 10) as i_iType_10,
                COUNT("bikeType") filter (where "bikeType" = 0) as i_bikeType_0,
                COUNT("bikeType") filter (where "bikeType" = 1) as i_bikeType_1,
                COUNT("bikeType") filter (where "bikeType" = 2) as i_bikeType_2,
                COUNT("bikeType") filter (where "bikeType" = 3) as i_bikeType_3,
                COUNT("bikeType") filter (where "bikeType" = 4) as i_bikeType_4,
                COUNT("bikeType") filter (where "bikeType" = 5) as i_bikeType_5,
                COUNT("bikeType") filter (where "bikeType" = 6) as i_bikeType_6,
                COUNT("bikeType") filter (where "bikeType" = 7) as i_bikeType_7,
                COUNT("bikeType") filter (where "bikeType" = 8) as i_bikeType_8
            FROM "SimRaAPI_incident" INNER JOIN "SimRaAPI_parsedfiles" SRAp on "SimRaAPI_incident".filename = SRAp."fileName"
            WHERE region = %s) i, (
            SELECT
                COUNT(*) as p_count,
                COUNT(gender) filter (where gender = 1) as p_gender_male,
                COUNT(gender) filter (where gender = 2) as p_gender_female,
                COUNT(gender) filter (where gender = 3) as p_gender_other,
                COUNT(birth) filter (where birth = 1 and gender = 1) as p_birth_1_male,
                COUNT(birth) filter (where birth = 1 and gender = 2) as p_birth_1_female,
                COUNT(birth) filter (where birth = 1 and gender = 3) as p_birth_1_other,
                COUNT(birth) filter (where birth = 2 and gender = 1) as p_birth_2_male,
                COUNT(birth) filter (where birth = 2 and gender = 2) as p_birth_2_female,
                COUNT(birth) filter (where birth = 2 and gender = 3) as p_birth_2_other,
                COUNT(birth) filter (where birth = 3 and gender = 1) as p_birth_3_male,
                COUNT(birth) filter (where birth = 3 and gender = 2) as p_birth_3_female,
                COUNT(birth) filter (where birth = 3 and gender = 3) as p_birth_3_other,
                COUNT(birth) filter (where birth = 4 and gender = 1) as p_birth_4_male,
                COUNT(birth) filter (where birth = 4 and gender = 2) as p_birth_4_female,
                COUNT(birth) filter (where birth = 4 and gender = 3) as p_birth_4_other,
                COUNT(birth) filter (where birth = 5 and gender = 1) as p_birth_5_male,
                COUNT(birth) filter (where birth = 5 and gender = 2) as p_birth_5_female,
                COUNT(birth) filter (where birth = 5 and gender = 3) as p_birth_5_other,
                COUNT(birth) filter (where birth = 6 and gender = 1) as p_birth_6_male,
                COUNT(birth) filter (where birth = 6 and gender = 2) as p_birth_6_female,
                COUNT(birth) filter (where birth = 6 and gender = 3) as p_birth_6_other,
                COUNT(birth) filter (where birth = 7 and gender = 1) as p_birth_7_male,
                COUNT(birth) filter (where birth = 7 and gender = 2) as p_birth_7_female,
                COUNT(birth) filter (where birth = 7 and gender = 3) as p_birth_7_other,
                COUNT(birth) filter (where birth = 8 and gender = 1) as p_birth_8_male,
                COUNT(birth) filter (where birth = 8 and gender = 2) as p_birth_8_female,
                COUNT(birth) filter (where birth = 8 and gender = 3) as p_birth_8_other,
                COUNT(birth) filter (where birth = 9 and gender = 1) as p_birth_9_male,
                COUNT(birth) filter (where birth = 9 and gender = 2) as p_birth_9_female,
                COUNT(birth) filter (where birth = 9 and gender = 3) as p_birth_9_other,
                COUNT(birth) filter (where birth = 10 and gender = 1) as p_birth_10_male,
                COUNT(birth) filter (where birth = 10 and gender = 2) as p_birth_10_female,
                COUNT(birth) filter (where birth = 10 and gender = 3) as p_birth_10_other,
                COUNT(birth) filter (where birth = 11 and gender = 1) as p_birth_11_male,
                COUNT(birth) filter (where birth = 11 and gender = 2) as p_birth_11_female,
                COUNT(birth) filter (where birth = 11 and gender = 3) as p_birth_11_other,
                COUNT(birth) filter (where birth = 12 and gender = 1) as p_birth_12_male,
                COUNT(birth) filter (where birth = 12 and gender = 2) as p_birth_12_female,
                COUNT(birth) filter (where birth = 12 and gender = 3) as p_birth_12_other,
                COUNT(birth) filter (where birth = 13 and gender = 1) as p_birth_13_male,
                COUNT(birth) filter (where birth = 13 and gender = 2) as p_birth_13_female,
                COUNT(birth) filter (where birth = 13 and gender = 3) as p_birth_13_other
            FROM "SimRaAPI_profile" WHERE "regionSpoken" = %s
            ) p
                ''', [region, region, region])
        columns = [col[0] for col in cursor.description]
        return HttpResponse(json.dumps([dict(zip(columns, row)) for row in cursor.fetchall()][0]), content_type = 'application/json; charset=utf8')
