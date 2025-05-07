from geopy.distance import geodesic

# fonction qui calcule la distance entre deux points A et B de coordonées respectives latA, longA et latB, longB


def calcul_distance(latA : int, longA : int, latB : int, longB : int) -> int:
    return geodesic((latA,longA),(latB,longB)).km

# Exemple :
# Coordonnées de Paris : latA=48.866669, longA=2.33333
# Coordonnées de Nice : latB=43.70000, longB=7.25000
# calcul_distance(latA,longA,latB,longB) = 687.7 km
