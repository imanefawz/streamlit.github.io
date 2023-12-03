import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import pandas as pd
from jenkspy import jenks_breaks

# Charger les données géospatiales depuis le fichier GeoParquet
path_to_geoparquet = "OUTPUT1500.geoparquet"
gdf = gpd.read_parquet(path_to_geoparquet)

st.set_page_config(
    page_title="Visualisation",
    page_icon="🌍",
    layout="wide",  
)

# Titre de l'application
st.markdown("<h1 style='font-size:24px;'>Une Carte de MAROC</h1>", unsafe_allow_html=True)


def jenks_classifier(data, column, k=5):
    values = data[column].values
    breaks = jenks_breaks(values, k)
    return breaks

# Sidebar pour la sélection de l'option (Attribut/Propriété)
option = st.sidebar.radio("Choisir une option", ("Attribut", "Propriété"))
# Récupérer les paramètres d'URL actuels
params = st.experimental_get_query_params()
if option == "Attribut":
    # Liste des attributs pour le choix
    attributs = ['temperature', 'pression_atmosph', 'pluviometrie']
    selected_attribute = st.sidebar.selectbox("Sélectionner un attribut", attributs)

    # Liste des jours pour le choix
    jours = [6, 5, 4, 3, 2, 1, 0]
    selected_day = st.sidebar.selectbox("Sélectionner un jour", jours)

    # Filtrer les données en fonction de l'attribut et du jour sélectionnés
    selected_column_day = f'{selected_attribute}jour{selected_day}'
    filtered_data = gdf[gdf[selected_column_day] >= 0]

    # Classer les valeurs en utilisant la méthode de Jenks
    breaks = jenks_classifier(filtered_data, selected_column_day, k=5)

    # Créer une carte Folium centrée sur la moyenne des coordonnées des géométries
    m = folium.Map(location=[gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()], zoom_start=4)

    # Définir l'échelle pour les symboles proportionnels
    scale = filtered_data[selected_column_day].max()
 # En fonction des conditions, ajuster le contenu de la page
    if selected_attribute != 'temperature' or selected_day != 6:
    # Changer les paramètres d'URL
     params["op"] = f"{selected_attribute}_{selected_day}"

    # Rafraîchir la page pour appliquer les changements d'URL
     if st.experimental_rerun() is not None:
        st.experimental_set_query_params(**params)
        st.experimental_rerun()
    # Ajouter les données à la carte en tant que symboles proportionnels
    for idx, row in filtered_data.iterrows():
        popup = f"{selected_column_day}: {row[selected_column_day]}"
        
        # Assigner une couleur en fonction de la classe Jenks
        color = '#f1eef6' if row[selected_column_day] <= breaks[1] else \
                '#bdc9e1' if row[selected_column_day] <= breaks[2] else \
                '#74a9cf' if row[selected_column_day] <= breaks[3] else \
                '#2b8cbe' if row[selected_column_day] <= breaks[4] else \
                '#045a8d'  

        folium.CircleMarker(
            location=[row['geometry'].y, row['geometry'].x],
            radius= 5,  # Ajuster l'échelle pour la taille des symboles
            popup=popup,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
        ).add_to(m)
    # Convertir les valeurs de la colonne en nombres flottants
    gdf[selected_column_day] = gdf[selected_column_day].astype(float)

    # Diviser les données en 5 classes
    nb_classes = 5
    class_bins = [gdf[selected_column_day].quantile(i / nb_classes) for i in range(nb_classes + 1)]
    colors = ['#f1eef6', '#bdc9e1', '#74a9cf', '#2b8cbe', '#045a8d']  # Autre jeu de couleurs

    
    # Définir la colormap
    colormap = folium.LinearColormap(colors=colors, vmin=gdf[selected_column_day].min(), vmax=gdf[selected_column_day].max())
    
    # Ajouter manuellement les classes à la carte Folium
    colormap.add_to(m)

   # En fonction des conditions, ajuster le contenu de la page
    if selected_attribute != 'temperature' or selected_day != 6:
    # Changer les paramètres d'URL
      params["op"] = f"{selected_attribute}_{selected_day}"

    # Rafraîchir la page pour appliquer les changements d'URL
      st.experimental_set_query_params(**params)
      st.experimental_rerun()

else:
    # Liste des propriétés pour le choix
    proprietes = [ 'humidité', 'Reflectance']
    selected_property = st.sidebar.selectbox("Sélectionner une propriété", proprietes)

    # Classer les valeurs en utilisant la méthode de Jenks
    breaks = jenks_classifier(gdf, selected_property, k=5)

    # Créer une carte Folium centrée sur la moyenne des coordonnées des géométries
    m = folium.Map(location=[gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()], zoom_start=4)

      # Définir les couleurs pour les classes
    colors = ['#f1eef6', '#bdc9e1', '#74a9cf', '#2b8cbe', '#045a8d']

    # Ajouter les données à la carte avec des couleurs pour les classes
    for idx, row in gdf.iterrows():
        popup = f"{selected_property}: {row[selected_property]}"
        
        # Assigner une couleur en fonction de la classe Jenks
        color = '#f1eef6' if row[selected_property] <= breaks[1] else \
                '#bdc9e1' if row[selected_property] <= breaks[2] else \
                '#74a9cf' if row[selected_property] <= breaks[3] else \
                '#2b8cbe' if row[selected_property] <= breaks[4] else \
                '#045a8d'
       
        value = row[selected_property]

        folium.CircleMarker(
            location=[row['geometry'].y, row['geometry'].x],
            radius=5,
            popup=popup,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
        ).add_to(m)
    # Convertir les valeurs de la colonne en nombres flottants
    gdf[selected_property] = gdf[selected_property].astype(float)

    # Diviser les données en 5 classes
    nb_classes = 5
    class_bins = [gdf[selected_property].quantile(i / nb_classes) for i in range(nb_classes + 1)]
    colors = ['#f1eef6', '#bdc9e1', '#74a9cf', '#2b8cbe', '#045a8d']  # Autre jeu de couleurs

    
    # Définir la colormap
    colormap = folium.LinearColormap(colors=colors, vmin=gdf[selected_property].min(), vmax=gdf[selected_property].max())
    
    # Ajouter manuellement les classes à la carte Folium
    colormap.add_to(m)
   # En fonction des conditions, ajuster le contenu de la page
    if selected_property != 'humidité':
    # Changer les paramètres d'URL
      params["op"] = f"{selected_property}"

    # Rafraîchir la page pour appliquer les changements d'URL
      st.experimental_set_query_params(**params)
      st.experimental_rerun()

    
# Afficher la carte dans Streamlit
folium_static(m ,width=1000, height=600)

