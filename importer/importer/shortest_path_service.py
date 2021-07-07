import requests
import json


def query_shortest_path_server(start, end):
    """Retrieves the shortest path between a start and an end point
    by querying a local graphhopper server.

    Parameters
    ----------
    start : Point
        Coordinate where the trajectory starts.
    end : Point
        End coordinate of the trajectory.
    """
    url = f"http://localhost:8989/route?vehicle=bike&point={start[1]},{start[0]}&point={end[1]},{end[0]}&points_encoded=false"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    coordinates = json.loads(response.text)["paths"][0]["points"]["coordinates"]
    return coordinates
