from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.serializers import ModelSerializer
from .models import Ride, Incident, ParsedFiles, OsmWaysLegs


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
        fields = ('osmId', 'streetName', 'postalCode', 'highwayName', 'count', 'score', 'weekdayCount', 'morning_count', 'evening_count')

