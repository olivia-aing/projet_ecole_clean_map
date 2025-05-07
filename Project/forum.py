from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3
from functionsDB import *

app = Flask(__name__)

def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(file) 
        db.execute("PRAGMA foreign_keys = ON") # pour activer les dépendances FK
    cur = db.cursor()
    return db, cur

#Pour l'instant pour accéder au forum, il faut rentrer l'identifiant de la localisation, puis après je vais chercher l'identifiant de la discussion 
# et je redirige vers cette page
@app.route("/forum", methods=['POST','GET'])
def redir_forum():
    if request.method == 'POST':
        lat=request.form.get('latitude')
        lon=request.form.get('longitude')
        cur=get_db()[1]
        locationid= cur.execute('SELECT location_id FROM locations WHERE (latitude,longitude)=(?,?)',(lat,lon)).fetchone()
        if not locationid:
            return redirect("/add")
        else:
            locationid=locationid[0]
            discussion_id = cur.execute("SELECT discussion_id FROM discussions WHERE location_id=? ", (locationid,)).fetchone()
            discussion_id = discussion_id[0]
            return redirect(f"/forum/{discussion_id}") 
    else:
        return render_template('redirection.html')
    
    
@app.route("/forum/<discussionid>", methods=["POST","GET"])
def forum(discussionid):
    if request.method == 'POST':
        message = request.form.get('message')
        add_message(get_db(),message,discussionid)
        tab=get_db()[1]
        table=tab.execute('SELECT * FROM messages')
        return render_template("forum.html",discussion_id=discussionid, data=table)
    else:
        tab=get_db()[1]
        table=tab.execute('SELECT * FROM messages WHERE discussion_id=discussionid')
        return render_template("forum.html", data=table)
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    
app.run(host='localhost', port=5000, debug=True)


@app.route("/connexion", methods=["GET","POST"])
def connexion():
    message=''
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cur=get_db()[1]
        user = cur.execute('SELECT * FROM users WHERE username = ?',(username,)).fetchone()
        if user:
            if check_password_hash(user[2],password):
                message='connexion réussie'
                flash(message)
                login_user(user, remember=True)
                return redirect("/home")
            else:
                message='mot de passe incorrect'
                        
        else:
            message="nom d'utilisateur incorrect ou inexistant"
        
        
    flash(message)
    return render_template("login.html")   



@app.route("/deconnexion")
@login_required
def deconnexion():
    logout_user()
    return render_template('connexion.html')

@app.route("/inscription", methods=["POST","GET"])
def inscription():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        cur = get_db()[1]
        usernames= cur.execute('SELECT username FROM users')
        if username in usernames:
            flash("nom d'utilisateur déjà utilisé, veuillez en saisir un nouveau")
        if password1 != password2:
            flash("le mot de passe n'est pas identique, veuillez vérifier le mot de passe")
        if len(username)<1:
            flash("le nom d'utilisateur ne peut pas être vide")
        if len(email)<6:
            flash('adresse mail invalide, la longueur doit être supérieur à 5 caractères')
        else:
            add_user(get_db(), username, generate_password_hash(password1,method='pbkdf2:sha1'),email)
            new_user=cur.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
            login_user(new_user, remember=True)
            flash('Compte crée avec succès')
            return redirect('/home')
    else:
        return render_template('inscription.html')