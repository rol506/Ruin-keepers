from flask import Flask, render_template, g, request, url_for, redirect
from SETTINGS import web_app_secret_key, web_app_debug
import os
import sqlite3
from FDataBase import FDataBase

app = Flask("ruinKeeper")
app.config.update(SECRET_KEY=web_app_secret_key)
app.config.update(DEBUG=web_app_debug)
app.config.update(DATABASE=os.path.join(app.root_path, "flsite.db"))

menu = [
        {
            "title": "Главная",
            "url": "/home"
        },
        {
            "title": "Мероприятия",
            "url": "/events/events"
        },
        {
            "title": "Прогулки",
            "url": "/events/walks"
        }
        #{
        #    "title": "Вход/Регистрация",
        #    "url": "/login"
        #},
        #{
        #    "title": "Запись",
        #    "url": "/create"
        #} 
]

def connect_db():
    db = sqlite3.connect(app.config.get("DATABASE"))
    db.row_factory = sqlite3.Row
    return db

def create_db():
    db = connect_db()
    with app.open_resource("sq_db.sql", "r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, "link_db"):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()

@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    return render_template("index.html", menu=menu)

#@app.route("/events")
#def event_choose():
    #db = FDataBase(get_db())
    #return render_template("event_choose.html", menu=menu, title="мероприятия")

@app.route("/events/events/register", methods=["POST", "GET"])
def register_event():
    return render_template("register_event.html", menu=menu)

@app.route("/events/events", methods=["POST", "GET"])
def events():

    if request.method == "POST":
        return redirect(url_for("register_event"))

    return render_template("events.html", menu=menu)

@app.route("/events/walks", methods=["POST", "GET"])
def walks():
    return render_template("walks.html", menu=menu)

@app.errorhandler(404)
def error_404(error): 
    return render_template("error_404.html", menu=menu)


if __name__ == "__main__":
    app.run("0.0.0.0", port=4221, debug=app.config.get("DEBUG"))
