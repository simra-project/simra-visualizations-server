"""Library of different filter functions.

Methods
-------
apply_smoothing_filters()
    apply_acc_filter()
    apply_rdp_filter()
apply_removal_filters()
    apply_short_distance_filter()
    apply_short_duration_filter()
    apply_high_avg_speed_filter()
    apply_user_forgot_to_stop_filter()
"""

from importer.settings import *
from rdp import rdp
from geopy.distance import great_circle


def apply_smoothing_filters(ride):
    """Reduces the data points of ride.

    Parameters
    ----------
    ride : Ride
        Ride entity to be filtered.

    Returns
    -------
    Ride
        Ride entity with fewer data but similar accuracy.
    """
    ride = apply_acc_filter(ride)
    ride = apply_rdp_filter(ride)
    return ride


def apply_removal_filters(ride):
    """Checks whether one of four filters apply.

    Parameters
    ----------
    ride : Ride
        Ride entity to be filtered.

    Returns
    -------
    bool
        True, if the trajectory can't be used for further calucations
        because one of the filters triggered.
    """
    ride_distance = calc_dist(ride.raw_coords_filtered)
    ride_duration = (ride.timestamps[-1] - ride.timestamps[0]).seconds
    return (
        apply_short_distance_filter(ride_distance)
        | apply_short_duration_filter(ride_duration)
        | apply_high_avg_speed_filter(ride_distance, ride_duration)
        | apply_user_forgot_to_stop_filter(ride)
    )


def apply_acc_filter(ride):
    len_before = len(ride.raw_coords)
    mask = [acc > MIN_ACCURACY for acc in ride.accuracies]
    ride.raw_coords_filtered = filter_by_mask(ride.raw_coords, mask)
    ride.timestamps_filtered = filter_by_mask(ride.timestamps, mask)
    print(
        "Accuracy filter filtered {} coordinates.".format(
            len_before - len(ride.raw_coords_filtered)
        )
    )
    return ride


def apply_rdp_filter(ride):
    len_before = len(ride.raw_coords_filtered)
    mask = rdp(ride.raw_coords_filtered, RDP_EPSILON, return_mask=True)
    ride.raw_coords_filtered = filter_by_mask(
        ride.raw_coords_filtered, [not boolean for boolean in mask]
    )
    ride.timestamps_filtered = filter_by_mask(
        ride.timestamps_filtered, [not boolean for boolean in mask]
    )
    print(
        "RDP filter filtered {} coordinates.".format(
            len_before - len(ride.raw_coords_filtered)
        )
    )
    return ride


def filter_by_mask(array, mask):
    return [i for (i, remove) in zip(array, mask) if not remove]


def apply_short_distance_filter(dist):
    if dist < MIN_RIDE_DISTANCE:
        print("Ride filtered due to short distance ({}m).".format(dist))
        return True
    else:
        return False


def apply_short_duration_filter(duration):
    if duration < MIN_RIDE_DURATION:
        print("Ride filtered due to short duration ({}sec).".format(duration))
        return True
    else:
        return False


def apply_high_avg_speed_filter(distance, duration):
    if duration <= 0:
        return True
    avg_speed = (distance / duration) * 3.6
    if avg_speed > MAX_RIDE_AVG_SPEED:
        print("Ride filtered due to high average speed ({}km/h).".format(duration))
        return True
    else:
        return False


#   heuristic approach
#
#   ride will be classified as 'forgot to stop' when User does not
#   exceed $MIN_DISTANCE_TO_COVER_IN_5_MIN in 5min (300sec) (300*6000millis)
#
#   5min in 3sec steps = 100steps
#
def apply_user_forgot_to_stop_filter(ride):
    for i in range(len(ride.raw_coords)):
        if i + 100 < len(ride.raw_coords):
            dist = calc_dist(ride.raw_coords[i : i + 100])
        else:
            break
        if dist < MIN_DISTANCE_TO_COVER_IN_5_MIN:
            print(
                "Ride filtered due to user forgot to stop recording (user only covered {}m in ~5min).".format(
                    dist
                )
            )
            return True
    return False


def calc_dist(coords):
    dist = 0.0
    for index, coord in enumerate(coords):
        if index + 1 < len(coords):
            dist += great_circle(coord, coords[index + 1]).meters
    return dist
