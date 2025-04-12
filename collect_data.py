import osmnx as ox
import os


def get_ordinal(n):
    """
    gen a list of arrondissement indexes
    :param n: 
    :return: 
    """
    if 10 <= n % 100 <= 20:
        suffix = "ème"
    else:
        suffix = {1: "er", 2: "ème", 3: "ème"}.get(n % 10, "ème")
    return f"{n}{suffix}"


def get_place_profile(place):
    print(f"Collecting geospatial data of {place}")
    folderout = f'data/{place}'
    os.makedirs(folderout, exist_ok=True)

    try:
        roads = ox.graph_from_place(place, network_type='all')
        ox.save_graphml(roads, f'{folderout}/roads.graphml')
    except Exception as e:
        print(f"Warning: Unable to fetch road network for {place}. {e}")

    feature_tags = {
        'public_transport': {'public_transport': True},
        'healthcare': {'amenity': ['hospital', 'pharmacy']},
        'education': {'amenity': ['school', 'university']},
        'emergency_services': {'amenity': ['police', 'fire_station', 'clinic']},
        'commerce': {'shop': True},
        'employment_centers': {'office': True, 'industrial': True}
    }

    for feature_name, tags in feature_tags.items():
        try:
            feature_data = ox.features_from_place(place, tags=tags)
            feature_data.to_file(f'{folderout}/{feature_name}.geojson', driver='GeoJSON')
        except Exception as e:
            print(f"Warning: No {feature_name} features found for {place}. Skipping. {e}")


arrondissement_numbers = [get_ordinal(i) for i in range(1, 12)]

for an in arrondissement_numbers:
    place = an + ' arrondissement, Cotonou'
    admin_a = ox.geocode_to_gdf(place)  #administrative arrondissement
    get_place_profile(place)
    admin_a.to_file('data/' + place + '/admin_boundaries.geojson', driver='GeoJSON')
    print(an)
