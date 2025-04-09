from flask import Flask, render_template, g, request, request_started, url_for, redirect, flash, session
from SETTINGS import web_app_secret_key, web_app_debug
import os
import sqlite3
from FDataBase import FDataBase
import datetime

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
            "title": "Галерея",
            "url": "/events/gallery"
        }
]

def getSliderPaths(configFileName):
    with open(configFileName, "r") as f:
        ls = f.read().replace("\n", "")
        return ls.split(",")

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
    return render_template("index.html", menu=menu, slides=getSliderPaths("main-slide-config.txt"))

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
        lunch = request.form.get("lunch")

        db = FDataBase(connect_db())

        db.addUser(eventID, name, telegram, phone, birth, lunch)
        #TODO message to the user "You have successfully registered for the event"

@app.route("/events/events/register/pay", methods=["POST", "GET"])
def payment():

    name = session.get("name")
    birth = session.get("birth")
    telegram = session.get("telegram")
    phone = session.get("phone")
    eventID = session.get("eventID")
    lunch = session.get("lunch")

    if not (name and birth and telegram and phone and eventID):
        print("Invalid data!")
        return redirect(url_for("index"))

    if request.method == "POST":
        session.clear()
        process_request()
        flash("Вы успешно зарегистрировались на мероприятие!", "info")
        return redirect(url_for("index"))

    db = FDataBase(get_db())
    ev = db.getEventByID(eventID)

    eventType = "Мероприятие"

    cost = ev["cost"] / 100

    lunchCost = ev["lunchCost"] if lunch else 0

    return render_template("pay.html", event=ev, eventType=eventType, name=name, phone=phone, telegram=telegram, birth=birth, cost=cost,
                           eventID=eventID, lunchCost=lunchCost/100, lunch=lunch)

@app.route("/events/events/register", methods=["POST", "GET"])
@app.route("/events/events/register/<eventID>", methods=["POST", "GET"])
def register_event(eventID=None):

    db = FDataBase(get_db())

    eventSelected = eventID is not None

    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        fathername = request.form.get("fathername")

        birth = request.form.get("birth")
        telegram = request.form.get("telegram")
        phone = request.form.get("phone")
        lunch = request.form.get("lunch")

        lunch = 0 if not lunch else 1

        eventID = request.form.get("eventID") if eventID is None else eventID

        if eventID == "None":
            flash("Пожалуйста выберите мероприятие", "info")
            return redirect(url_for("register_event", eventID=eventID if eventSelected else None))

        if " " in name or " " in surname or " " in fathername:
            flash("ФИО не должно содержать пробелов!", "info")
            return redirect(url_for("register_event", eventID=eventID if eventSelected else None))
        name = name + " " + surname + " " + fathername

        if " " in telegram:
            flash("Имя пользователя Telegram не может содержать пробелов!", "info")
            return redirect(url_for("index"))

        if "@" in telegram:
            telegram = telegram[1:]

        if " " in phone:
            flash("Номер телефона не может содержать пробелов!", "info")
            return redirect(url_for("index"))

        if db.getPhoneCount(phone, eventID) > 0:
            flash("Номер телефона уже зарегистрирован на это мероприятие!", "info")
            return redirect(url_for("register_event", eventID=eventID if eventSelected else None))

        if db.getTelegramCount(telegram, eventID) > 0:
            flash("Имя пользователя Telegram уже зарегистрировано на это мероприятие!", "info")
            return redirect(url_for("register_event", eventID=eventID if eventSelected else None))

        session["name"] = name
        session["birth"] = birth
        session["telegram"] = telegram
        session["phone"] = phone
        session["eventID"] = eventID
        session["lunch"] = lunch

        return redirect(url_for("payment"))

    return render_template("register.html", menu=menu, events=db.getEvents(), eventID=eventID)

@app.route("/events/events", methods=["POST", "GET"])
def events():

    if request.method == "POST":
        evID = request.form.get("id")
        return redirect(url_for("register_event", eventID=evID))

    db = FDataBase(get_db())

    date = datetime.datetime.now().strftime("%Y-%m")
    events = db.getEvents()
    return render_template("events.html", menu=menu, events=events)

@app.route("/events/day/<year>/<month>/<day>", methods=["POST", "GET"])
def eventsByDate(year, month, day):

    if request.method == "POST":
        id = request.form.get("id")
        return redirect(url_for("register_event", eventID=id))

    if (int(day) < 10):
        day = "0"+str(day)

    if (int(month) < 10):
        month = "0"+str(month)

    date = year + "-" + month + "-" + day
    db = FDataBase(connect_db())
    events = db.getEventsByDate(date)
    return render_template("list_events.html", menu=menu, title="Мероприятия "+date, events=events, maxlen=0)

@app.route("/events/walks", methods=["POST", "GET"])
def walks():
    return render_template("walks.html", menu=menu)
@app.route("/events/gallery", methods=["POST", "GET"])
def gallery():
    return render_template("gallery.html", menu=menu, slides=getSliderPaths("gallery-slide-config.txt"))

@app.errorhandler(404)
def error_404(error): 
    return render_template("error_404.html", menu=menu)

if __name__ == "__main__":
    app.run("0.0.0.0", port=4221, debug=app.config.get("DEBUG"))
