import folium
from folium.plugins import MousePosition, Search, Geocoder
import sqlite3 


def crea_map():
    fileDB = "data/CleanMap_DB.db" # depuis le rep Project

    m = folium.Map(location=(48.6833, 6.2), zoom_start=12)


    MousePosition().add_to(m)

    db = sqlite3.connect(fileDB) 
    cur = db.cursor()
    locations_list = cur.execute('SELECT * FROM locations').fetchall()
    # récupère toutes les lignes de la table locations dans une liste de tuples

    for l in locations_list : 
        # pour chaque tuple correspondant à 1 lieu :
        if l[3]=='notClean' : # verifie le statut actuel du lieu
            location_id = cur.execute("SELECT location_id FROM locations WHERE latitude = ? AND longitude = ? ;", (l[1],l[2])).fetchone()
            discussion_id = cur.execute("SELECT MAX(discussion_id) FROM discussions WHERE location_id = ? ;", (location_id[0],)).fetchone()
            folium.Marker(
            location=[l[1], l[2]],
            popup=f"<a href='/forum/{discussion_id[0]}'>Forum</a>",
            tooltip="À nettoyer !",
            icon=folium.Icon(color = "red", icon="cloud")
            ).add_to(m)

        else :
            folium.Marker(
            location=[l[1], l[2]],
            tooltip="Nettoyé !",
            popup=f"Date de dernier nettoyage : {l[4]}",
            icon=folium.Icon(color = "green", icon="cloud")
            ).add_to(m)

    db.close()




    Geocoder().add_to(m)

    m.save('templates/map.html')

    c0 = open('templates/map.html', 'r')
    c1 = c0.read()
    c0.close()
    c2 = open('templates/map.html', 'w')
    c2.write("{% extends 'root.html' %}\n{% block title %}Carte{% endblock %}\n{% block content %} ")
    c2.close()
    c3 = open('templates/map.html','a')
    c3.write(c1)
    c3.write("{% endblock %}")

    return 'map.html'

