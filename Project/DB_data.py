from functionsDB import *
from werkzeug.security import generate_password_hash

file = "data/CleanMap_DB.db" # depuis le rep Project

con = sqlite3.connect(file) 
print(con)
cur = con.cursor()
print(cur)
con.execute("PRAGMA foreign_keys = ON") # pour activer les FK et le 'on delete cascade'



########## USERS 


users = [('JohnDoe', 'qmoizrfhu', 'john.doe@gmail.com'),
('Jane', 'qmzeofghi', 'jane.smith@free.fr'),
('Sam_Jones', 'qslegr!hzçgh', 'sam.jones@laposte.net'),
('Emma', 'qapmpqkdc,', 'emma.wilson@yahoo.fr'), 
('AliceInWonderland', 'cqmoreiguh', 'alice.jackson@orange.fr'),
('B0B', 'bzlmgiouzleo', 'bob.smith@email.fr'),
('Carol_davis', 'zlgeoqbhiuv', 'carol.davis@gmail.com'),
('David_wilson', 'pozcfreiug', 'david.wilson@gmail.com') ]
# tkt personne a vu les mdp en clair


cur.execute("DELETE FROM users ;")

for user in users :
    add_user((con, cur), user[0], generate_password_hash(user[1],method='pbkdf2:sha1'),user[2])



########## PINS 


locationsWithDate = [(1, 48.697863, 6.184729, 'notClean', '2023-11-20'),
(2, 48.693385, 6.194008, 'Clean', '2023-12-05'), 
(3, 48.659764, 6.15366, 'Clean', '2023-12-13'),
(4, 48.66219, 6.156385, 'Clean', '2023-12-27'),
(5, 48.655023, 6.156931, 'Clean', '2024-01-10') ]

locationsWithoutDate = [(6,  48.663222, 6.145414, 'notClean'), 
(7, 48.680328, 6.170809, 'notClean'),
(8, 48.664125, 6.177638, 'notClean'),
(9, 48.668970, 6.153688, 'notClean') ]

cur.execute("DELETE FROM locations ;")

for location in locationsWithDate :
    with con : 
        cur.execute("INSERT INTO locations (location_id, latitude, longitude, clean_status, last_cleaned_date) VALUES (?,?,?,?,?)",
                (location[0], location[1], location[2], location[3], location[4]))

for location in locationsWithoutDate :
    with con : 
        cur.execute("INSERT INTO locations (location_id, latitude, longitude, clean_status) VALUES (?,?,?,?)",
                (location[0], location[1], location[2], location[3]))



########## DISCUSSIONS


discussions = [
(1, 'La roseraie du parc de la Pépinière', 1),
(2, 'Rives de la Meurthe (promenade de Kanazawa)', 2),
(3, 'Jardin botanique Jean Marie Pelt : Alpinium', 3),
(4, 'Jardin botanique - zone des plantes médicinales', 4),
(5, 'Aire de jeux du parc de la Sapinière', 5),
(6, 'La cabane du parc de Brabois', 6),
(7, 'Parc Sainte-Marie', 7),
(8, "Parc Richard Pouille : l'aire de jeux", 8),
(9, 'Parc de Rémicourt (à côté de TN)', 9) ]

cur.execute("DELETE FROM discussions ;")
for discussion in discussions :
    with con : 
        cur.execute("INSERT INTO discussions (discussion_id, discussion_title, location_id) VALUES (?,?,?)",
                (discussion[0], discussion[1], discussion[2]))



########## MESSAGES  


# uniquement les discussions 1, 6, 7, 8, 9 sont en cours       
messages = [
("2024-01-09 19:30:00", "Salut !", 1, 'Emma'),
("2024-01-09 19:42:00", "Hey !", 1, 'AliceInWonderland'),
("2024-01-12 09:30:00", "On se retrouve au parc pour le nettoyage dans la semaine ?", 1, 'Emma'),
("2024-01-12 09:35:00", "Je suis pas encore sûre d'être dispo cette semaine", 1, 'Jane'),
("2024-01-15 14:30:00", "Je peux le 20! J'apporterai des sacs poubelles et des gants.", 1, 'JohnDoe'),
("2024-01-15 18:45:00", "Quelqu'un peut apporter des rafraîchissements pour le nettoyage au Parc de la Pépinière?", 1, 'B0B'),
("2024-01-16 09:00:00", "Jane, des mises à jour sur le nettoyage à venir ?", 1, 'Emma'),
("2024-01-16 09:30:00", "Oui samedi je serai là", 1, 'Jane'),

("2023-12-27 10:45:00", "Nettoyage au parc de Brabois ce week-end, qui vient ?", 6, 'Jane'),
("2023-12-28 10:30:00", "David_wilson, nous avons besoin de votre aide pour organiser le nettoyage du parc de Brabois.", 6, 'Jane'),
("2023-12-28 19:45:00", "Sam_Jones, veuillez vous coordonner avec les bénévoles pour le nettoyage du parc de Brabois.", 6, 'David_wilson'),
("2023-12-29 13:15:00", "Jane, nous comptons sur votre leadership pour le parc de Brabois.", 6, 'Sam_Jones'),

("2024-01-12 08:30:00", "Rendez-vous au parc Sainte Marie demain à 10h pour des travaux d'entretien.", 7, 'Emma'),
("2024-01-12 16:00:00", "Carol_davis, n'oubliez pas d'apporter vos outils de jardinage.", 7, 'Sam_Jones'),
("2024-01-12 18:30:00", "Je n'oublierai pas ! Des suggestions pour rendre le parc Sainte Marie plus durable ?", 7, 'Carol_davis'),

("2024-01-05 12:00:00", "Nous avons besoin de plus de bénévoles pour le nettoyage du parc Richard Pouille.", 8, 'Sam_Jones'),
("2024-01-07 14:00:00", "Le nettoyage est reporté au week-end prochain.", 8, 'Emma'),
("2024-01-10 12:00:00", "Jane, peux-tu créer un événement Facebook pour le nettoyage du parc Richard Pouille ?", 8, 'Sam_Jones'),

("2023-12-28 11:15:00", "AliceInWonderland, veuillez confirmer votre disponibilité pour le nettoyage.", 9, 'B0B'),
("2023-12-28 17:15:00", "Je serai là", 9, 'AliceInWonderland'),
("2023-12-30 10:00:00", "Merci ! Nous apprécions votre dévouement à la cause!", 9, 'JohnDoe') ]

cur.execute("DELETE FROM messages ;")
for message in messages :
    with con : 
        cur.execute("INSERT INTO messages (m_datetime, m_text, discussion_id, username) VALUES (?,?,?,?)",
                (message[0], message[1], message[2], message[3]))