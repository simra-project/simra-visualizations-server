import math
from datetime import timedelta
from geopy.distance import great_circle
from postgis import LineString


def process_surface(ride, accelerations):
    raw_coords = ride.raw_coords
    timestamps = ride.timestamps
    first_five_seconds = []
    for X, Y, Z, ts, coords in accelerations:
        if ts - accelerations[0][3] > timedelta(seconds=5):
            break
        first_five_seconds.append((X, Y, Z))

    A5 = [sum(y) / len(y) for y in zip(*first_five_seconds)]  # get average of accelerations in first 5 seconds of ride

    sliding_window_size = 5  # seconds per direction
    every_x_seconds = 2.5
    current_max_idx = 0
    IRI = []
    ride_sections = []
    in_window = []
    for i in range(len(raw_coords)):
        current = raw_coords[i]
        ls = raw_coords[i: i + 2]
        ts = timestamps[i]
        while in_window and ts - in_window[0][3] > timedelta(seconds=sliding_window_size):
            in_window.remove(in_window[0])
        while current_max_idx < len(accelerations) and accelerations[current_max_idx][3] - ts < timedelta(seconds=sliding_window_size):
            A = accelerations[current_max_idx][:-2]
            d = math.sqrt(A5[0] ** 2 + A5[1] ** 2 + A5[2] ** 2)
            if d == 0:
                d = 1
            avs = (A[0] * A5[0] + A[1] * A5[1] + A[2] * A5[2]) / d
            if len(in_window) > 1:
                dt = (in_window[-1][3] - in_window[-2][3]).total_seconds()
            else:
                dt = 0.1
            in_window.append(accelerations[current_max_idx] + (abs(avs * dt ** 2 / 2),))
            current_max_idx += 1
        if len(in_window) < 2:
            continue
        Sh = great_circle(in_window[0][4], in_window[-1][4]).meters
        if Sh > 0:
            iri = sum(list(zip(*in_window))[5]) / Sh
            if not (IRI and (ts - IRI[-1][1]).total_seconds() < every_x_seconds):
                IRI.append((iri, ts, current, Sh))
            if len(ls) == 2:
                ride_sections.append((LineString(ls, srid=4326), iri))
    return IRI, ride_sections
