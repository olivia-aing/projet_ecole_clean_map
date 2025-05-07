"""
L'application à lancer pour pouvoir faire des tests sur le site
Commencez bien par ouvrir le dossier "Project" dans vscode pour qu'on soit au même endroit !
"""

# Importation des modules nécessaires

from flask import Flask, render_template, redirect, g, request, flash,  session
from markupsafe import Markup
from werkzeug.security import check_password_hash,generate_password_hash
# from flask_login import login_required
import sqlite3
import os
from functionsDB import *
from carte import *
import re


# Connexion à la base de données

def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(file) 
        db.execute("PRAGMA foreign_keys = ON") # pour activer les dépendances FK
    cur = db.cursor()
    return db, cur

"""
-------------------------------------------------------
-------------------------------------------------------
-----------------A P P L I C A T I O N-----------------
-------------------------------------------------------
-------------------------------------------------------
"""

# Bases

app = Flask(__name__)
app.secret_key = os.urandom(24)


"""
Créer une page web : 

@app.route('/url'):
def url():
    # Pour prendre des données dans la db (à quelques variations près)
    db, cur = get_db()
    datlist = cur.execute('Commande SQL').fetchall()

    # Pour faire afficher la page avec le template dans le dossier templates
    return render_template('url.html',nom_variable_dans_template = datlist)      
"""

@app.route('/', methods=['GET'])
def root():
    db, cur = get_db()
    total = cur.execute('SELECT COUNT(*) FROM locations').fetchall()
    propre = cur.execute("SELECT COUNT(*) FROM locations WHERE clean_status='Clean'").fetchall()
    sessionName=session.get('user_id')
    if sessionName is not None:
        uid = True
    else:
        uid = False
    return render_template('home.html', total=total, propre=propre, uid=uid)

@app.route('/home', methods=['GET'])
def home():
    db, cur = get_db()
    total = cur.execute('SELECT COUNT(*) FROM locations').fetchall()
    propre = cur.execute("SELECT COUNT(*) FROM locations WHERE clean_status='Clean'").fetchall()
    sessionName=session.get('user_id')
    if sessionName is not None:
        uid = True
    else:
        uid = False
    return render_template('home.html', total=total, propre=propre, uid=uid)

@app.route('/about')
def about():
    return render_template('a_propos.html')

@app.route('/map')
def map():
    return render_template(crea_map())

    
@app.route("/notclean/<locationID>")
def changeNotCleanStatus(locationID) : 
    discussionID = notClean_location(get_db(), locationID)
    return redirect(f"/forum/{discussionID}")

@app.route("/clean/<discussion>")
def changeCleanStatus(discussion) : 
    Clean_location(get_db(), discussion)
    return redirect(f"/home")


@app.route("/add", methods=['post', 'get'])
def add():
    afficher =''
    sessionName=session.get("user_id")
    if sessionName is not None:
        con, cur = get_db()
        if request.method == 'POST':
            if request.form['latitude'] and request.form['longitude'] and request.form['forum_title'] :
                latitude = request.form['latitude']
                longitude = request.form['longitude']
                title = request.form['forum_title']
                test = no_point_close(get_db(), latitude, longitude)
                
                if test == 'True' : # pas de point à moins de 30m
                    add_new_pin(get_db(),[latitude,longitude], title) # on ajoute les valeurs dans la table
                    locationID = cur.execute("SELECT location_id FROM locations WHERE latitude = ? AND longitude= ? ;", (latitude, longitude)).fetchone()
                    locationID = locationID[0]
                    discussionId = cur.execute("SELECT discussion_id FROM discussions WHERE location_id = ? ;", (locationID,)).fetchone()
                    afficher = Markup(f"""Le pin a bien été ajouté ! Vous pouvez trouver le forum <a href="/forum/{discussionId[0]}">ici</a> """)
                
                else : # il existe un point à moins de 30m -> TEST = location_id du lieu proche
                    if location_is_clean(get_db(), test) : #si le lieu est propre
                        afficher = Markup(f"""Un pin existe déjà à moins de 30m. Il est noté comme propre et le forum a donc été fermé. <br> 
                                          Vous pouvez rouvrir la discussion pour nettoyer ce lieu en cliquant <a href="/notclean/{test}">ici</a>.""")
                    else : 
                        title, discussionId = cur.execute("SELECT discussion_title, discussion_id FROM discussions WHERE location_id = ? ;", (test,)).fetchone()
                        afficher = Markup(f"""Un pin existe déjà à moins de 30m. Pour aller sur la discussion correspondante "{title}" cliquez <a href="/forum/{discussionId}">ici</a>""")
            else : 
                afficher = "Il manque une information pour créer le pin."

            flash(afficher)
            return redirect('/add')
        return render_template("add_pin.html")
    else:
        afficher='Vous devez être connecté pour accéder à cette page'
        flash(afficher)
        return redirect('/login')


@app.route("/forum", methods=['POST','GET'])
def redir_forum():
    sessionName=session.get('user_id')
    if sessionName is not None:
        # if request.method == 'POST':
        #     lat=request.form.get('latitude')
        #     lon=request.form.get('longitude')
        #     cur=get_db()[1]
        #     locationid= cur.execute('SELECT location_id FROM locations WHERE (latitude,longitude)=(?,?)',(lat,lon)).fetchone()
        #     if not locationid:
        #         #flash('Pas de forum lié à cette localisation, veuillez ajouter un pin pour le créer')
        #         return redirect("/add")  #verification de l'existence d'un forum pour les coordonnées données, si non: redirection vers la page d'ajout
        #     else:
        #         locationid=locationid[0]
        #         discussion_id = cur.execute("SELECT discussion_id FROM discussions WHERE location_id=? ", (locationid,)).fetchone()
        #         discussion_id = discussion_id[0]
        #         return redirect(f"/forum/{discussion_id}") 

        cur=get_db()[1]
        dataClean = cur.execute("""SELECT l.latitude, l.longitude, d.discussion_id, d.discussion_title
                       FROM locations l INNER JOIN discussions d 
                       ON l.location_id = d.location_id 
                       WHERE l.clean_status = 'Clean' ;""").fetchall()
        dataNotClean = cur.execute("""SELECT l.latitude, l.longitude, d.discussion_id, d.discussion_title, l.location_id
                       FROM locations l INNER JOIN discussions d 
                       ON l.location_id = d.location_id 
                       WHERE l.clean_status = 'notClean' ;""").fetchall()
        return render_template('redirection.html', tableAlreadyClean = dataClean, tableToBeCleaned = dataNotClean)
    else:
        afficher='Vous devez être connecté pour accéder à cette page'
        flash(afficher)
        return redirect('/login')

    
@app.route("/forum/<discussionid>", methods=["POST","GET"])
def forum(discussionid):
    sessionName=session.get('user_id')
    if sessionName is not None:   
        if request.method == 'POST':
            message = request.form.get('message')
            tab=get_db()[1]
            username= tab.execute('SELECT username FROM users WHERE id =?',(sessionName,)).fetchone()[0]
            add_message(get_db(),message,discussionid,username)
            table=tab.execute('SELECT * FROM messages WHERE discussion_id=?',(discussionid,))
            return render_template("forum.html",discussion_id=discussionid, data=table,)
        else:
            tab=get_db()[1]
            table=tab.execute('SELECT * FROM messages WHERE discussion_id=?',(discussionid,))
            return render_template("forum.html",discussion_id=discussionid, data=table)
    else:
        afficher='Vous devez être connecté pour accéder à cette page'
        flash(afficher)
        return redirect('/login')

@app.route("/login", methods=["GET","POST"])
def connexion():
    message=''
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cur=get_db()[1]
        user = cur.execute('SELECT * FROM users WHERE username = ?',(username,)).fetchone()
        if user:
            if check_password_hash(user[2],password):
                session.clear()
                session['user_id']=user[0]
                message='Connexion réussie'
                flash(message)
                return redirect("/home")
            else:
                message="mot de passe ou nom d'utilisateur incorrect"
                        
        else:
            message="mot de passe ou nom d'utilisateur incorrect"
        
        
    flash(message)
    return render_template("login.html")   



@app.route("/logout")
# @login_required
def deconnexion():
    sessionName=session.get('user_id')
    if sessionName is not None:    
        session.clear()
        message='Vous avez été déconnecté'
        flash(message)
        return redirect('/login')
    else:
        afficher='Vous devez être connecté pour accéder à cette page'
        flash(afficher)
        return redirect('/login')

@app.route("/sign_up", methods=["POST","GET"])
def inscription():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        cur = get_db()[1]
        usernames= cur.execute('SELECT username FROM users').fetchall()
        mails= cur.execute('SELECT email FROM users').fetchall()
        t = True
        mailex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for i in range(len(usernames)-1):
            if username == usernames[i][0]:
                t = False
        if not t:
            flash("Nom d'utilisateur déjà utilisé, veuillez en saisir un nouveau")
            return render_template('inscription.html')
        if len(password1)<=8:
            flash("Le mot de passe de passe ne peut pas faire moins de 8 caractères")
            return render_template('inscription.html')
        if password1 != password2:
            flash("Le mot de passe n'est pas identique, veuillez vérifier le mot de passe")
            return render_template('inscription.html')
        if len(username)<1:
            flash("Le nom d'utilisateur ne peut pas être vide")
            return render_template('inscription.html')
        if not (re.fullmatch(mailex, email)):
            flash('Adresse mail invalide')
            return render_template('inscription.html')
        t = True
        for i in range(len(mails)-1):
            if email == mails[i][0]:
                t = False
        if not t:
            flash("Adresse mail déjà utilisée")
            return render_template('inscription.html')
        else:
            add_user(get_db(), username, generate_password_hash(password1,method='pbkdf2:sha1'),email)
            new_user=cur.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
            session.clear()
            session['user_id']=new_user[0]
            #message='connexion réussie'
            flash('Compte créé avec succès')
            return redirect('/home')
    else:
        return render_template('inscription.html')

# Fermeture de la base de données

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Lancement de l'application

app.run(host='0.0.0.0', port=8080, debug=True, ssl_context='adhoc')
# ssl_context = adhoc : pour passer en https pour la géolocalisation


