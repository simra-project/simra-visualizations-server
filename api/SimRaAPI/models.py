"""Collection of entity classes.

Classes
----------
ParsedFiles
Ride
Profile
Incident
RideSegmentSurface
RideSegmentVelocity
OsmWaysJunctions
OsmWaysLegs
OsmWaysLargeJunctions
"""

from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField


class ParsedFiles(models.Model):
    """A class used to represent a parsed CSV file of a bicycle ride.

    Attributes
    -------
    filename : CharField
        The name of the CSV file the ride was imported from.
    fileType : CharField
        Either 'profile' or 'ride'.
    region : CharField
        The region the recorded ride was done in, e.g. 'Berlin'.
    importTimeStamp : DateTimeField
        The exact time stamp of when the file was imported into the database.
    """

    fileName = models.CharField(max_length=32)
    fileType = models.CharField(max_length=32)
    region = models.CharField(max_length=32, default="unknown")
    importTimestamp = models.DateTimeField(auto_now=True)


class Ride(models.Model):
    """A class used to represent a bicycle ride.

    Attributes
    -------
    timestamps : ArrayField(DateTimeField)
        The time stamps of the GPS measurements.
    filename : CharField
        The name of the CSV file the ride was imported from.
    geom : LineStringField
        Raw GPS data of the ride.
    start : PointField
        The coordinate the trajectory was started from.
    end : PointField
        The end coordinate of the trajectory.
    legs : ArrayField(BigIntegerField)
        IDs of legs the map matched ride is covering.
    """

    timestamps = ArrayField(models.DateTimeField())
    filename = models.CharField(max_length=32)
    geom = models.LineStringField()
    start = models.PointField(null=True)
    end = models.PointField(null=True)
    legs = ArrayField(models.BigIntegerField(), default=list)


class Profile(models.Model):
    """A class used to represent a user profile of the SimRa application.

    Attributes
    -------
    birth : IntegerField
        Birth year group.
    gender : IntegerField
        1 = Male, 2 = Female, 3 = Other
    region : IntegerField
    regionSpoken : CharField
    experience : IntegerField
        Experience as a cyclist in year groups.
    numberOfRides : IntegerField
    duration : IntegerField
    numberOfIncidents : IntegerField
    length : IntegerField
    idle : IntegerField
    behaviour : IntegerField
        How much the user follows the traffic rules. 0 - 5, where 0 is 'never' and 5 is 'always'.
    numberOfScary : IntegerField
    """

    birth = models.IntegerField()
    gender = models.IntegerField()
    region = models.IntegerField()
    regionSpoken = models.CharField(max_length=32, default="unknown")
    experience = models.IntegerField()
    numberOfRides = models.IntegerField()
    duration = models.IntegerField()
    numberOfIncidents = models.IntegerField()
    length = models.IntegerField()
    idle = models.IntegerField()
    behaviour = models.IntegerField()
    numberOfScary = models.IntegerField()


class Incident(models.Model):
    """A class used to represent a near miss incident.

    Attributes
    -------
    rideTimestamp : DateTimeField
        Time stamp of when the incident happened.
    bikeType : IntegerField
        Type of the bicycle used.
    childCheckbox : BooleanField
        False, if no child was being transported, true otherwise.
    trailerCheckbox : BooleanField
        False, if no trailer is attached to the bike, true otherwise.
    pLoc : IntegerField
        Location of the phone during the ride.
    incident : IntegerField
        TODO:
    iType : IntegerField
        The other participant involved in the incident.
    scary : BooleanField
        True, if the incident was scary, false otherwise.
    desc : TextField
        Description of the incident.
    filename : CharField
        The name of the CSV file the incident was saved in.
    ride : ForeignKey(Ride)
        The ride in which the incident happened.
    geom : PointField
        The coordinates where the incident happened.
    """

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
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, null=True)
    geom = models.PointField()


class RideSegmentSurface(models.Model):
    """The surface quality of a ride segment.

    Attributes
    -------
    geom : LineStringField
        The coordinates of the ride segment.
    score : FloatField
        A score representing the road quality.
    """

    geom = models.LineStringField()
    score = models.FloatField()


class RideSegmentVelocity(models.Model):
    """The velocity of a ride segment.

    Attributes
    -------
    geom : LineStringField
        The coordinates of the ride segment.
    velocity : FloatField
    """

    geom = models.LineStringField()
    velocity = models.FloatField()


class OsmWaysJunctions(models.Model):
    """A class used to represent a junction of the OSM service.

    Attributes
    ----------
    point : PointField
        The coordinate of the junction in the OSM service.
    """

    point = models.PointField()


class OsmWaysLegs(models.Model):
    """A class used to represent a leg of the OSM service.

    Attributes
    ----------
    osmId : BigIntegerField
        The of the leg in the OSM service.
    geom : GeometryField
        Coordinates of the leg.
    streetName : TextField
    postalCode : TextField
    highwayName : TextField
    count : IntegerField
    score : FloatField
    score_array : ArrayField(FloatField)
    velocity : FloatField
    velocity_array : ArrayField(FloatField)
    weekdayCount : IntegerField
    morningCount : IntegerField
    eveningCount : IntegerField
    normalIncidentCount : IntegerField
    scaryIncidentCount : IntegerField
    """

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
    morningCount = models.IntegerField(default=0)
    eveningCount = models.IntegerField(default=0)
    normalIncidentCount = models.IntegerField(default=0)
    scaryIncidentCount = models.IntegerField(default=0)


class OsmLargeJunctions(models.Model):
    """A class used to represent a large junction of the OSM service.

    Attributes
    ----------
    point : PointField
        The coordinate of the junction.
    count : IntegerField
    totalDuration : IntegerField
    avgDuration : FloatField
    """

    point = models.PointField(spatial_index=True)
    count = models.IntegerField(default=0)
    totalDuration = models.BigIntegerField(default=0)
    avgDuration = models.FloatField(default=0)
