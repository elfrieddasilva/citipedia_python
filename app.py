import osmnx as ox
import pandas as pd
from flask import Flask, request, jsonify

from geospacial_utils import get_optimal_path, find_best_place_to_live
from livability_compute import gen_geodataframe_from_saved_data, gen_livability_index_for_data_frame

app = Flask(__name__)
df = pd.read_csv("cotonou_features_data.csv")
gdf_admin = gen_geodataframe_from_saved_data()
gdf_index = gen_livability_index_for_data_frame(df)


@app.route("/best_path", methods=["GET"])
def best_path():
    """Finds the best path between two coordinates using OSM data"""
    origin_lat = request.args.get("origin_lat", type=float)
    origin_lng = request.args.get("origin_lng", type=float)
    dest_lat = request.args.get("dest_lat", type=float)
    dest_lng = request.args.get("dest_lng", type=float)

    try:
        print(f"Received coordinates: Origin({origin_lat}, {origin_lng}), Destination({dest_lat}, {dest_lng})")

        optimal_path = get_optimal_path((origin_lat, origin_lng), (dest_lat, dest_lng))
        suitable_living_places = find_best_place_to_live(gdf_index, gdf_admin, dest_lat, dest_lng)

        # Select only the desired columns and convert to JSON
        living_index_data = suitable_living_places[
            ['Place', 'Unified Livability Index', 'Distance', 'Weighted Score']].to_dict('records')

        # Rename columns for the JSON response (optional)
        for item in living_index_data:
            item['living_index'] = item.pop('Unified Livability Index')
            item['place'] = item.pop('Place')
            item['distance'] = item.pop('Distance')
            item['score'] = item.pop('Weighted Score')

        return jsonify({"optimal_routes": optimal_path, "best_places":living_index_data})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
