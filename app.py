import pandas as pd
from flask import Flask, request, jsonify
from functools import lru_cache

from geospacial_utils import get_optimal_path, find_best_place_to_live, get_coordinates
from livability_compute import gen_geodataframe_from_saved_data, gen_livability_index_for_data_frame

app = Flask(__name__)
df = pd.read_csv("cotonou_features_data.csv")
gdf_admin = gen_geodataframe_from_saved_data()
gdf_index = gen_livability_index_for_data_frame(df)

place_coordinates = {}
for place in gdf_index['Place']:
    place_coordinates[place] = get_coordinates(place, gdf_admin)

@lru_cache(maxsize=128)
def get_optimal_path_cached(origin_lat, origin_lng, dest_lat, dest_lng, network_type):
    return get_optimal_path((origin_lat, origin_lng), (dest_lat, dest_lng), network_type=network_type)


@app.route("/best_path", methods=["GET"])
def best_path():
    dest_lat = request.args.get("dest_lat", type=float)
    dest_lng = request.args.get("dest_lng", type=float)
    transportation = request.args.get("transportation", type=str)  # Changed to str

    try:
        if transportation is None:
            transportation = "all"

        suitable_living_places = find_best_place_to_live(gdf_index, gdf_admin, dest_lat, dest_lng)
        living_index_data = suitable_living_places[['Place', 'Unified Livability Index', 'Distance', 'Weighted Score']].to_dict('records')

        for item in living_index_data:
            item['living_index'] = item.pop('Unified Livability Index')
            item['place'] = item.pop('Place')
            item['distance'] = item.pop('Distance')
            item['score'] = item.pop('Weighted Score')
            coordinates = place_coordinates.get(item['place'])
            if coordinates:
                item['latitude'] = coordinates['latitude']
                item['longitude'] = coordinates['longitude']

                item['optimal_path'] = get_optimal_path_cached(coordinates['latitude'], coordinates['longitude'], dest_lat, dest_lng, transportation)
            else:
                item['latitude'] = None
                item['longitude'] = None
                item['optimal_path'] = None

        return jsonify({"best_places": living_index_data})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
