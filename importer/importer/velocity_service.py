from importer.importer.stop_service import find_stops_in_raw_coords
from importer.importer.settings import COVERED_DISTANCE_INSIDE_STOP_FOR_VELOCITY_THRESHOLD
import copy
from geopy.distance import great_circle


def process_velocity(ride, cur):
    slow_sections = find_stops_in_raw_coords(ride, COVERED_DISTANCE_INSIDE_STOP_FOR_VELOCITY_THRESHOLD)
    continuous_ride = remove_slow_sections(ride, slow_sections)
    total_distance = calc_total_distance(continuous_ride.raw_coords)
    total_duration = (continuous_ride.timestamps[-1] - continuous_ride.timestamps[0]).seconds
    v = total_distance / total_duration
    a = 12

def remove_slow_sections(ride, slow_sections):
    continuous_ride = copy.deepcopy(ride)
    indices_to_remove = []
    for section in slow_sections:
        indices_to_remove.append(section.indices)
        for i in range(section.indices[-1], len(continuous_ride.timestamps)):
            continuous_ride.timestamps[i] = continuous_ride.timestamps[i] - section.duration
    indices_to_remove = [item for sublist in indices_to_remove for item in sublist]  # flatten
    continuous_ride.raw_coords = [v for i, v in enumerate(continuous_ride.raw_coords) if i not in indices_to_remove]
    continuous_ride.timestamps = [v for i, v in enumerate(continuous_ride.timestamps) if i not in indices_to_remove]
    return continuous_ride


def calc_total_distance(coords):
    total_dist = 0
    for i, coord in enumerate(coords):
        if i + 1 < len(coords):
            total_dist += great_circle(coord, coords[i + 1]).meters
    return total_dist
