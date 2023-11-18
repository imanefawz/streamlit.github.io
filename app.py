import streamlit as st
import geopandas as gpd

# Titre de l'application Streamlit
st.title("Visualisation des données GeoParquet")

# Charger les données GeoParquet
path_to_output_geoparquet = "OUTPUT1000.geoparquet"  # Mettez ici le chemin absolu vers votre fichier
data = gpd.read_parquet(path_to_output_geoparquet)

# Afficher les données géographiques
st.map(data)
