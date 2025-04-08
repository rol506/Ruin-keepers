from flask import Flask, render_template, g, request, request_started, url_for, redirect, flash, session
from SETTINGS import web_app_secret_key, web_app_debug
import os
import sqlite3
from FDataBase import FDataBase
from datetime import datetime

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
        },
        {
            "title": "Галерея",
            "url": "/events/gallery"
        }
]

def connect_db():
    db = sqlite3.connect(app.config.get("DATABASE"))
    db.row_factory = sqlite3.Row
    return db

def create_db():
    db = connect_db()
    with open("sq_db.sql", "r") as f:
        db.cursor().executescript(f.read())
        #print(f.read())
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

def process_request():

    if request.method == "POST":
        name = request.form.get("name")
        birth = request.form.get("birth")
        telegram = request.form.get("telegram")
        phone = request.form.get("phone")
        eventID = request.form.get("eventID")

        db = FDataBase(connect_db())

        db.addUser(eventID, name, telegram, phone, birth)
        #TODO message to the user "You have successfully registered for the event"

@app.route("/events/events/register/pay", methods=["POST", "GET"])
def payment():

    name = session.get("name")
    birth = session.get("birth")
    telegram = session.get("telegram")
    phone = session.get("phone")
    eventID = session.get("eventID")

    if not (name and birth and telegram and phone and eventID):
        print("Invalid data!")
        return redirect(url_for("index"))

    if request.method == "POST":
        session.clear()
        process_request()
        flash("Вы успешно зарегистрировались на мероприятие!", "info")
        print("successfully registered (", name, ")", "for the event id ", eventID)
        return redirect(url_for("index"))

    db = FDataBase(get_db())
    ev = db.getEventById(eventID)

    eventType = "Мероприятие"

    cost = ev["cost"] / 100

    return render_template("pay.html", event=ev, eventType=eventType, name=name, phone=phone, telegram=telegram, birth=birth, cost=cost, eventID=eventID)

@app.route("/events/events/register", methods=["POST", "GET"])
@app.route("/events/events/register/<eventID>", methods=["POST", "GET"])
def register_event(eventID=None):

    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        fathername = request.form.get("fathername")

        birth = request.form.get("birth")
        telegram = request.form.get("telegram")
        phone = request.form.get("phone")

        eventID = request.form.get("eventID")

        if eventID == "None":
            flash("Пожалуйста выберите мероприятие", "info")
            return redirect(url_for("register_event"))

        if " " in name or " " in surname or " " in fathername:
            flash("ФИО не должно содержать пробелов!", "info")
            return redirect(url_for("register_event"))
        name = name + " " + surname + " " + fathername

        if " " in telegram:
            flash("Имя пользователя Telegram не может содержать пробелов!", "info")
            return redirect(url_for("index"))

        if "@" in telegram:
            telegram = telegram[1:]

        if " " in phone:
            flash("Номер телефона не может содержать пробелов!", "info")
            return redirect(url_for("index"))

        session["name"] = name
        session["birth"] = birth
        session["telegram"] = telegram
        session["phone"] = phone
        session["eventID"] = eventID

        return redirect(url_for("payment"))

    db = FDataBase(get_db())

    return render_template("register.html", menu=menu, events=db.getEvents(), eventID=eventID)

@app.route("/events/events", methods=["POST", "GET"])
def events():

    if request.method == "POST":
        return redirect(url_for("register_event"))

    db = FDataBase(get_db())

    return render_template("events.html", menu=menu, events=db.getEvents())

@app.route("/events/day/<day>", methods=["POST", "GET"])
def eventsByDay(day):

    if request.method == "POST":
        id = request.form.get("id")
        return redirect(url_for("register_event", eventID=id))

    if (int(day) < 10):
        day = "0"+str(day)

    date = datetime.today().strftime('%Y-%m-')
    date += day
    db = FDataBase(get_db())
    events = db.getEventsByDate(date)
    return render_template("list_events.html", menu=menu, title="Мероприятия "+date, events=events, maxlen=0)

@app.route("/events/walks", methods=["POST", "GET"])
def walks():
    return render_template("walks.html", menu=menu)
@app.route("/events/gallery", methods=["POST", "GET"])
def gallery():
    return render_template("gallery.html", menu=menu)

@app.errorhandler(404)
def error_404(error): 
    return render_template("error_404.html", menu=menu)

if __name__ == "__main__":
    app.run("0.0.0.0", port=4221, debug=app.config.get("DEBUG"))
