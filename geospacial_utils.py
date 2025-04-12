import osmnx as ox
from shapely.geometry import Point
import networkx as nx
from geopy.distance import geodesic


def get_coordinates(place_name, gdf):
    """Distance calculation between two locations inside a graph dataframe """
    try:
        place = gdf[gdf['Place'] == place_name].iloc[0]
        return {'latitude': place['lat'], 'longitude': place['lon']}
    except IndexError:
        print(f"Place '{place_name}' not found in the GeoDataFrame.")
        return None


def calculate_distance_between(origin, destination):
    """
    Calculate the distance between two points origin(lat,lng) and
    destination(lat,lng)
    :param origin:
    :param destination:
    :return:
    """
    return geodesic(origin, destination).kilometers


def find_arrondissement(latitude, longitude, gdf):
    """
    Find the arrondissement within which a location is
    :param latitude:
    :param longitude:
    :param gdf:
    :return:
    """
    point = Point(longitude, latitude)
    for index, row in gdf.iterrows():
        if row['geometry'].contains(point):
            return row['Place']
    return None


def get_optimal_path(origin, destination, base_place="Cotonou, Bénin", network_type="drive"):
    G = ox.graph_from_place(base_place, network_type=network_type)
    nodes, edges = ox.graph_to_gdfs(G)
    minx, miny, maxx, maxy = nodes.total_bounds

    print(f"Graph bounding box: ({miny}, {minx}) to ({maxy}, {maxx})")
    print(f"Origin: {origin}, Destination: {destination}")
    if not G:
        raise ValueError("Graph could not be created for the given location")

    # Find the nearest nodes
    try:
        origin_node = ox.distance.nearest_nodes(G, X=origin[1], Y=origin[0], return_dist=False)
        destination_node = ox.distance.nearest_nodes(G, X=destination[1], Y=destination[0], return_dist=False)

        shortest_path = nx.shortest_path(G, origin_node, destination_node, weight='length')
        path_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]

        return path_coords
    except nx.NetworkXNoPath:
        print("No path found between origin and destination within the graph.")
        return None
    except Exception as e:
        print(f"Error during path calculation: {e}")
        return None


def calculate_distance_to_destination(place, gdf_admin, destination_latitude, destination_longitude):
    """
    Calculates the distance between a place and the destination.

    Args:
        place (str): Name of the place.
        gdf_admin (gpd.GeoDataFrame): GeoDataFrame containing geometry and place names.
        destination_latitude (float): Latitude of the destination.
        destination_longitude (float): Longitude of the destination.

    Returns:
        float: Distance in kilometers.
    """
    try:
        place_coordinates = get_coordinates(place, gdf_admin)
        if place_coordinates:
            origin = (place_coordinates['latitude'], place_coordinates['longitude'])
            destination = (destination_latitude, destination_longitude)
            distance = geodesic(origin, destination).kilometers
            return distance
        else:
            return float('inf')  # Return infinity if place coordinates not found
    except Exception as e:
        print(f"Error calculating distance for {place}: {e}")
        return float('inf')  # Return infinity in case of errors



def find_best_place_to_live(df_livability, gdf_admin, destination_latitude, destination_longitude, top_n=5):
    """
    Finds the best places to live based on livability index and distance to a destination.

    Args:
        df_livability (pd.DataFrame): DataFrame containing livability index for each place.
        gdf_admin (gpd.GeoDataFrame): GeoDataFrame containing geometry and place names.
        destination_latitude (float): Latitude of the destination.
        destination_longitude (float): Longitude of the destination.
        top_n (int, optional): Number of top places to return. Defaults to 5.

    Returns:
        pd.DataFrame: DataFrame with the top_n places, their livability index, and distance to the destination.
    """
    if 'Place' not in df_livability.columns:
        print("Error: 'Place' column not found in df_livability")


    # 1. Calculate distances
    df_livability['Distance'] = df_livability['Place'].apply(lambda place: calculate_distance_to_destination(place, gdf_admin, destination_latitude, destination_longitude))

    df_livability = df_livability[df_livability['Distance'] > 0]
    # 2. Calculate weighted score (combining livability and distance)
    df_livability['Weighted Score'] = df_livability['Unified Livability Index'] / df_livability['Distance']

    # 3. Sort by weighted score and select top places
    top_places = df_livability.sort_values(by=['Weighted Score'], ascending=False).head(top_n)

    return top_places[['Place', 'Unified Livability Index', 'Distance', 'Weighted Score']]


