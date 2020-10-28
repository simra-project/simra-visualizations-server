from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.serializers import ModelSerializer
from .models import Ride, Incident, ParsedFiles, OsmWaysLegs, Statistics


class RideSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Ride
        geo_field = 'geom'
        fields = ('filename',)


class IncidentSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Incident
        geo_field = 'geom'
        fields = ('rideTimestamp', 'bikeType', 'childCheckbox', 'trailerCheckbox', 'pLoc', 'incident', 'iType', 'scary', 'desc', 'filename')


class ParsedFilesSerializer(ModelSerializer):
    class Meta:
        model = ParsedFiles
        fields = ('fileName', 'fileType', 'importTimestamp')


class LegSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = OsmWaysLegs
        geo_field = 'geom'
        fields = ('osmId', 'streetName', 'postalCode', 'highwayName', 'count', 'score', 'weekdayCount', 'rushhourCount')


class StatisticsSerializer(ModelSerializer):
    class Meta:
        model = Statistics
        fields = ('r_count', 'r_meters', 'r_seconds', 'r_savedco2', 'r_avg_distance', 'r_avg_duration', 'r_avg_velocity',
                  'i_count', 'i_count_scary', 'i_count_child', 'i_count_trailer', 'i_incident_minus_1', 'i_incident_0',
                  'i_incident_1', 'i_incident_2', 'i_incident_3', 'i_incident_4', 'i_incident_5', 'i_incident_6', 'i_incident_7',
                  'i_incident_8', 'i_iType_minus_1', 'i_iType_0', 'i_iType_1', 'i_iType_2', 'i_iType_3', 'i_iType_4',
                  'i_iType_5', 'i_iType_6', 'i_iType_7', 'i_iType_8', 'i_iType_9', 'i_iType_10')