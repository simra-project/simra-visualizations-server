import gpxpy
import gpxpy.gpx
import requests


def map_match(ride):
    gpx_xml = create_gpx(ride.raw_coords_filtered)
    return query_map_match_server(gpx_xml)


def create_gpx(coords):
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for coord in coords:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(coord[1], coord[0]))

    return gpx.to_xml()


def query_map_match_server(gpx_xml):
    # curl -XPOST -H "Content-Type: application/gpx+xml" -d @route.gpx "localhost:8989/match?vehicle=bike&type=gpx&gps_accuracy=100"
    map_matched = []
    url = 'http://localhost:8989/match?vehicle=bike&type=gpx&gps_accuracy=50'
    headers = {'Content-Type': 'application/gpx+xml'}
    response = requests.post(url, data=gpx_xml, headers=headers)

    gpx = gpxpy.parse(response.text)

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                map_matched.append([point.longitude, point.latitude])
    return map_matched
