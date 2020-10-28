from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField


class ParsedFiles(models.Model):
    fileName = models.CharField(max_length=32)
    fileType = models.CharField(max_length=32)
    region = models.CharField(max_length=32, default="unknown")
    importTimestamp = models.DateTimeField(auto_now=True)


class Incident(models.Model):
    rideTimestamp = models.DateTimeField()
    bikeType = models.IntegerField()
    childCheckbox = models.BooleanField()
    trailerCheckbox = models.BooleanField()
    pLoc = models.IntegerField()
    incident = models.IntegerField()
    iType = models.IntegerField()
    scary = models.BooleanField()
    desc = models.TextField()
    filename = models.CharField(max_length=32)

    geom = models.PointField()


class Ride(models.Model):
    timestamps = ArrayField(models.DateTimeField())
    filename = models.CharField(max_length=32)
    geom = models.LineStringField()
    start = models.PointField(null=True)
    end = models.PointField(null=True)
    legs = ArrayField(models.BigIntegerField(), default=list)


class RideSegment(models.Model):
    geom = models.LineStringField()
    score = models.FloatField()


class OsmWaysJunctions(models.Model):
    point = models.PointField()


class OsmWaysLegs(models.Model):
    osmId = models.BigIntegerField()
    geom = models.GeometryField()
    streetName = models.TextField()
    postalCode = models.TextField()
    highwayName = models.TextField()
    count = models.IntegerField(default=0)
    score = models.FloatField(default=0)
    score_array = ArrayField(models.FloatField(), default=list)
    velocity = models.FloatField(default=0)
    velocity_array = ArrayField(models.FloatField(), default=list)
    weekdayCount = models.IntegerField(default=0)
    rushhourCount = models.IntegerField(default=0)


class OsmLargeJunctions(models.Model):
    point = models.PointField(spatial_index=True)
    count = models.IntegerField(default=0)
    totalDuration = models.BigIntegerField(default=0)
    avgDuration = models.FloatField(default=0)


class Statistics(models.Model):
    r_count = models.IntegerField()
    r_meters = models.FloatField()
    r_seconds = models.FloatField()
    r_savedco2 = models.FloatField()
    r_avg_distance = models.FloatField()
    r_avg_duration = models.FloatField()
    r_avg_velocity = models.FloatField()
    i_count = models.IntegerField()
    i_count_scary = models.IntegerField()
    i_count_child = models.IntegerField()
    i_count_trailer = models.IntegerField()
    i_incident_minus_1 = models.IntegerField()
    i_incident_0 = models.IntegerField()
    i_incident_1 = models.IntegerField()
    i_incident_2 = models.IntegerField()
    i_incident_3 = models.IntegerField()
    i_incident_4 = models.IntegerField()
    i_incident_5 = models.IntegerField()
    i_incident_6 = models.IntegerField()
    i_incident_7 = models.IntegerField()
    i_incident_8 = models.IntegerField()
    i_iType_minus_1 = models.IntegerField()
    i_iType_0 = models.IntegerField()
    i_iType_1 = models.IntegerField()
    i_iType_2 = models.IntegerField()
    i_iType_3 = models.IntegerField()
    i_iType_4 = models.IntegerField()
    i_iType_5 = models.IntegerField()
    i_iType_6 = models.IntegerField()
    i_iType_7 = models.IntegerField()
    i_iType_8 = models.IntegerField()
    i_iType_9 = models.IntegerField()
    i_iType_10 = models.IntegerField()

    class Meta:
        managed = False

