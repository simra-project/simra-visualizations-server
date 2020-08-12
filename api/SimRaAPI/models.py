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
