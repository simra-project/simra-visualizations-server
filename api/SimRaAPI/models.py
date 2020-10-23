from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField


class ParsedFiles(models.Model):
    fileName = models.CharField(max_length=32)
    fileType = models.CharField(max_length=32)
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

