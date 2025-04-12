import osmnx as ox
import os
import geopandas as gpd
import pandas as pd

"""
    Compute the key KPI like for each arrondissement
    to generate a livability index
    The KPIs are
    Public Transport
    Healthcare
    Education
    Emergency Services
    Commerce
    Employment Centers
"""

CRS = 32631 #CRS code used EPSG:32631,
#Between 0°E and 6°E, northern hemisphere between the equator and 84°N, onshore and offshore. Algeria. Andorra. Belgium. Benin. Burkina Faso. Denmark - North Sea. France. Germany - North Sea. Ghana. Luxembourg. Mali. Netherlands. Niger. Nigeria. Norway. Spain. Togo. United Kingdom (UK) - North Sea.
#More at epsg.io/32631

def characterize_arrondissement(place):
    """
        A function that get the available kpi data for an arrondissement
    :param place:
    :return:
    """
    folderin = 'data/' + place

    files = {
        "public_transport": "public_transport.geojson",
        "healthcare": "healthcare.geojson",
        "education": "education.geojson",
        "emergency_services": "emergency_services.geojson",
        "commerce": "commerce.geojson",
        "employment_centers": "employment_centers.geojson"
    }
    print(f"Collecting features data for {place}")
    def load_data(key):
        filepath = os.path.join(folderin, files[key])
        try:
            return gpd.read_file(filepath)
        except Exception as e:
            print(f"Warning: {key} data is missing or corrupted for {place}. Error: {e}")
            return None

    roads_graph = ox.load_graphml(folderin + '/roads.graphml') #Load road graph data
    public_transport = load_data("public_transport")
    healthcare = load_data("healthcare")
    education = load_data("education")
    emergency_services = load_data("emergency_services")
    commerce = load_data("commerce")
    employment_centers = load_data("employment_centers")

    try:
        edges = ox.graph_to_gdfs(roads_graph, nodes=False, edges=True)
        if edges.crs is None:
            raise ValueError("Road network edges are missing a CRS.")
        edges = edges.to_crs(CRS)

        road_length = edges['length'].sum() / 1000  # in km
        total_area = edges.unary_union.convex_hull.area / 1000 ** 2  # in km²
        road_density = road_length / total_area  # km/km²

    except Exception as e:
        print(f"Error computing road metrics for {place}: {e}")
        road_length = total_area = road_density = None

    # Compute feature densities (handling missing datasets)
    def safe_density(data):
        return len(data) / total_area if data is not None and total_area else None

    public_transport_density = safe_density(public_transport)
    healthcare_accessibility = safe_density(healthcare)
    education_accessibility = safe_density(education)
    emergency_services_density = safe_density(emergency_services)
    commerce_density = safe_density(commerce)
    employment_centers_density = safe_density(employment_centers)

    def zero_if_none(value):
        return value if value is not None else 0

    data = {
        "Place": zero_if_none(place),
        "Road Density": zero_if_none(road_density),
        "Public Transport Density": zero_if_none(public_transport_density),
        "Healthcare Accessibility": zero_if_none(healthcare_accessibility),
        "Education Accessibility": zero_if_none(education_accessibility),
        "Emergency Services Density": zero_if_none(emergency_services_density),
        "Retail Density": zero_if_none(commerce_density),
        "Employment Centers Density": zero_if_none(employment_centers_density)
    }

    return pd.DataFrame([data])

###Saving the relevant data to csv
arrondissements = [f for f in os.listdir('data') if '.' not in f]
arrf_all = [] #array of arrondissement features
for arr in arrondissements:
    arrf = characterize_arrondissement(arr) #retrieve feature for the place
    print(arr, len(arrf))
    arrf_all.append(arrf)
arrf_all = pd.concat(arrf_all).set_index('Place')

arrf_all.to_csv("cotonou_features_data.csv") #Save the data to csv format