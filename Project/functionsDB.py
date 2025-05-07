# à lancer depuis le rep Project pour accéder à Project/data/CleanMap_DB.db

import sqlite3
import time
from time import strftime
from calcul_distance import calcul_distance

file = "data/CleanMap_DB.db" # depuis le rep Project


####### ADD FUNCTIONS #######


def add_new_pin(getDB:tuple, coordinates:list, title:str):
    # add a new pin : adds a location linked to a discussion forum 
    # useful : define only once the locations' PK which is used by all tables (defines discussions' PK which defines messages' PK)
    # title : discussion's title defined by the user when adding the forum 
    con, cur = getDB

    location_id = cur.execute("SELECT location_id FROM locations ORDER BY location_id DESC LIMIT 1").fetchone()
    # renvoie un tuple d'un seul élément : (location_id,)
    if location_id is None : location_id = 1
    else : location_id = location_id[0]+1
    with con :
        add_location(cur, location_id, coordinates)
        add_discussion(cur, title, location_id)
    return 


def add_location(cur, id:int, coordinates:list): 
    # locations : location_id (PK), clean_status
    # coordinates = location_id : liste de 2 valeurs [latitude, longitude]
    cur.execute("INSERT INTO locations (location_id, latitude, longitude, clean_status) VALUES (?, ?, ?, 'notClean')",
                 (id, coordinates[0], coordinates[1]) )
    return 


def add_discussion(cur, title:str, location_fk):
    # discussions : discussion_id (PK), discussion_title, location_id (FK)
    cur.execute("INSERT INTO discussions (discussion_title, location_id) VALUES (?, ?)", 
                (title, location_fk) )
    return 

def add_message(getDB, text:str, discussion:int, username:str) :
    # text : str du message entier
    # discussion : PK du forum dans lequel l'utilisateur ajoute son message 
    # message_id (SERIAL INTEGER NOT NULL), m_datetime (timestamp), m_text (varchar)
    ## TODO
    con, cur = getDB 
    location_id = cur.execute("SELECT location_id FROM discussions WHERE discussion_id=? ", (discussion,)).fetchone()
    location_id = location_id[0]
    if not location_is_clean(getDB, location_id) : # la location est pas clean donc la discussion est en cours
        with con : 
            cur.execute("INSERT INTO messages (m_datetime, m_text, discussion_id, username) VALUES (?, ?, ?, ?)",
                     (strftime( "%Y-%m-%d %H:%M:%S", time.localtime() ), text, discussion, username) )
#     else : # la location est clean, la discussion est finie
#         return print("""Le lieu est propre donc la discussion a été archivée.
# Vous pouvez ajouter des messages à cette discussion en changeant le statut du lieu comme étant à nettoyer.""")
    return

def add_user(getDB, username:str, password:str, email:str) :
    # users : id, username, password, email
    ## TODO
    con, cur = getDB 
    with con : 
        cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                    (username, password, email) )
    return


####### UPDATE FUNCTIONS #######


def Clean_location(getDB, discussionID:int):
    # coordinates : [latitude, longitude]
    # when location has been cleaned : change status from 'notClean' to 'Clean'
    # & modify current date as the last date that place was cleaned
    # boutton pour modifier dans le forum/discussionID 
    # redirect vers statut qd le lieu est dit 'clean' puisque discussions et messages sont 
    con, cur = getDB 
    locationID = cur.execute("SELECT location_id FROM discussions WHERE discussion_id=? ;", 
                (discussionID,) ).fetchone()
    locationID = locationID[0]
    cur.execute("UPDATE locations SET clean_status = 'Clean', last_cleaned_date=? WHERE location_id = ? ;", (strftime("%Y-%m-%d", time.localtime()), locationID) )
    cur.execute("DELETE FROM messages WHERE discussion_id = ?;", (discussionID,) )
    con.commit()
    return 


def notClean_location(getDB, locationID:int) -> int :
    """Utilisé depuis /status : utilise le location_ID 
    le lieu correspondant à location_id est mis à jour avec le nouveau status 'NotClean'
    et la discussion précédente est réouverte"""
    con, cur = getDB 
    with con :
        cur.execute("UPDATE locations SET clean_status = 'notClean' WHERE location_id = ? ;", (locationID,) ) 
        discussionID = cur.execute("SELECT discussion_id FROM discussions WHERE location_id = ? ;", (locationID,) ).fetchone()
    return discussionID[0]


####### DELETE FUNCTIONS #######


def delete_location(getDB, id:list) :
    # locations : location_id (PK), latitude, longitude, clean_status
    con, cur = getDB 
    cur.execute("DELETE FROM locations WHERE location_id=(?)", (id,) )
    con.commit()
    return 

def delete_discussion(getDB, id:list) :
    con, cur = getDB 
    cur.execute("DELETE FROM discussions WHERE discussion_id=(?);", (id,) )
    con.commit()
    return 

def delete_message(getDB, id:int) :
    con, cur = getDB 
    cur.execute("DELETE FROM messages WHERE message_id=(?);", (id,) )
    con.commit()
    return 


####### SHOW FUNCTIONS #######



def show_locations(n=0):
    cur.execute("SELECT * FROM locations")
    rows = cur.fetchall()
    for row in rows[n:] :
        # for each of the n last rows from the table
        print(row)
    return


def show_discussions(n=0):
    cur.execute("SELECT * FROM discussions")
    rows = cur.fetchall()
    for row in rows[n:] :
        # for each of the n last rows from the table
        print(row)
    return


def show_messages(n=0):
    cur.execute("SELECT * FROM messages")
    rows = cur.fetchall()
    for row in rows[n:] :
        # for each of the n last rows from the table
        print(row)
    return


####### CHECK FUNCTIONS #######


def location_is_clean(getDB:tuple, id:int) :
    """True : the location is "Clean" 
    False : the location is "notClean" """
    con, cur = getDB 
    status = cur.execute("SELECT clean_status FROM locations WHERE location_id = ?", (id,)).fetchone()
    return status[0] == 'Clean'


def no_point_close(getDB, new_latitude, new_longitude) :
    """ pas de souci : 
    aucun point à moins de 30m -> TRUE
    sinon : 
    il y a au moins 1 point "proche" -> locationID """
    con, cur = getDB 
    all_coordinates = cur.execute("SELECT latitude, longitude FROM locations").fetchall()
    for LatLong in all_coordinates :
        # LatLong : [latitude, longitude] d'un seul point
        dist = calcul_distance(LatLong[0], LatLong[1], new_latitude, new_longitude)
        if dist < 0.030 : # distance entre 2 points inférieure à 30m
            locationID = cur.execute("SELECT location_id FROM locations WHERE latitude = ? AND longitude = ? ;", (LatLong[0], LatLong[1])).fetchone()
            locationID = locationID[0]
            return locationID
    return 'True' #sinon pour une locationID = 1 <=> True


######### TESTS #########

if __name__=='__main__' : 
    #verif de la connextion à la database : 
    con = sqlite3.connect(file) 
    print(con)
    cur = con.cursor()
    print(cur)
    con.execute("PRAGMA foreign_keys = ON") # pour activer les FK et le 'on delete cascade'

    getDB = (con, cur)

    coordinates = [48.680161, 6.181313]
    # coordinates2 = [48.657013, 6.144258]
    # delete_location(getDB, 1)
    # add_new_pin(getDB, coordinates, "Let's clean !")

    # Clean_location(getDB, 1)
    notClean_location()

    # add_message(getDB, "General Kenobi !", 1, 'test')

    # add_user(getDB, 'truc', 'sldekfhbgqlq', 'sleiryg@qcelgiu.com')
    # add_user(getDB, 'test', 'qlezbf', 'qkjerfv@lsieryg.com')
    # add_user(getDB, 'test', 'qjkezyfgq', 'qlize@qksegiyf.com')
    
    print("\nLOCATIONS : ")
    show_locations()
    print("\nDISCUSSIONS : ")
    show_discussions()
    print("\nMESSAGES : ")
    show_messages()
    print("\n")

    con.commit()
    con.close()