import os
import geopandas as gpd
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


"""
    Compute a livability index
        Find a suitable city administrative level and compute the quality of
        life in each area in a comparative way, scoring each area's livability
        from 1 to 10.
"""

 #Read the saved data frame

def gen_geodataframe_from_saved_data():
    gdf_admin = [] #save the geodataframe for each place
    for d in os.listdir('data'):
        if '.DS' not in d:
            gdf = gpd.read_file('data/' + d + '/admin_boundaries.geojson')
            gdf['Place'] = d
            gdf_admin.append(gdf)
    gdf_admin = pd.concat(gdf_admin)
    return gdf_admin

"""
    Computing a livability score for each dondissement
"""
def gen_livability_index_for_data_frame(df):
    numerical_features = df.drop('Place', axis=1) #Remove the place labels
    scaler = MinMaxScaler(feature_range=(1,10)) #A score ranging from 1 to 10

    df_normalized = pd.DataFrame(
        scaler.fit_transform(numerical_features),
        columns=numerical_features.columns,
        index=df.index
    )

    df_normalized['Place'] = df['Place']
    df_normalized = df_normalized[['Place'] + numerical_features.columns.tolist()]  # reorder column

    #Weights for the model
    weights = {
        'Road Density': 0.1,
        'Public Transport Density': 0.15,
        'Healthcare Accessibility': 0.1,
        'Education Accessibility': 0.1,
        'Emergency Services Density': 0.1,
        'Retail Density': 0.15,
        'Employment Centers Density': 0.1
    }

    for feature in df_normalized.columns[1:]:
        df_normalized[feature] = df_normalized[feature] * weights[feature] #multiplying the kpi data for each feature by the weight

    df_normalized['Unified Livability Index'] = df_normalized.iloc[:, 1:].sum(axis=1) # summing all the values of the features for each arrondissement

    scaler_index = MinMaxScaler(feature_range=(1, 10)) #defining a scaler to adjust the distribution

    df_normalized['Unified Livability Index'] = scaler_index.fit_transform(df_normalized[['Unified Livability Index']]) #adjusting the weights for the livability index

    df_normalized['Unified Livability Index'] = df_normalized['Unified Livability Index'].round(0)

    df_normalized[['Place', 'Unified Livability Index']].sort_values(by='Unified Livability Index', ascending=False)
    return df_normalized