import folium
from folium.plugins import MarkerCluster, MousePosition, Search, Geocoder
import webbrowser
import sqlite3 

fileDB = "data/CleanMap_DB.db" # depuis le rep Project

m = folium.Map(location=(48.6833, 6.2), zoom_start=12)

MousePosition().add_to(m)

icon_create_function = """\
function(cluster) {
    return L.divIcon({
    html: '<b>' + cluster.getChildCount() + '</b>',
    className: 'marker-cluster marker-cluster-large',
    iconSize: new L.Point(35, 35)
    });
}"""

marker_cluster = MarkerCluster(icon_create_function=icon_create_function).add_to(m)


####################################################################################################################
####################################################################################################################

""" Depuis le code de Lise pour les marqueurs : 

folium.Marker(
    location=[48.657013, 6.144258],
    tooltip="A nettoyer !",
    icon=folium.Icon(color = "red", icon="cloud"),
).add_to(marker_cluster)

folium.Marker(
    location=[48.720775, 6.197381],
    tooltip="Nettoyé !",
    popup="date de dernier néttoyage : ",
    icon=folium.Icon(color = "green", icon="cloud"),
).add_to(m)
"""

db = sqlite3.connect(fileDB) 
cur = db.cursor()
locations_list = cur.execute('SELECT * FROM locations').fetchall()
# récupère toutes les lignes de la table locations dans une liste de tuples

for location in locations_list : 
    # pour chaque tuple correspondant à 1 lieu :
    if location[3]=='notClean' : # verifie le statut actuel du lieu
        folium.Marker(
        location=[location[1], location[2]],
        tooltip="À nettoyer !",
        icon=folium.Icon(color = "red", icon="cloud")
        ).add_to(m)

    else :
        folium.Marker(
        location=[location[1], location[2]],
        tooltip="Nettoyé !",
        popup=f"Date de dernier nettoyage : {location[4]}",
        icon=folium.Icon(color = "green", icon="cloud")
        ).add_to(m)

db.close()

###################################################################################################################
####################################################################################################################


Geocoder().add_to(m)


m.save('carte_cluster.html')

m.save('map.html')

webbrowser.open('map.html')