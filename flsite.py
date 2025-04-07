from flask import Flask, render_template
from flask_login import LoginManager
from SETTINGS import web_app_secret_key, web_app_debug

app = Flask("ruinKeeper")
app.config.update(SECRET_KEY=web_app_secret_key)
app.config.update(DEBUG=web_app_debug)

loginManager = LoginManager()
loginManager.init_app(app)

menu = [
        {
            "title": "Главная",
            "url": "/home"
        },
        {
            "title": "Мероприятия",
            "url": "/events"
        },
        {
            "title": "Вход/Регистрация",
            "url": "/login"
        },
        #{
        #    "title": "Запись",
        #    "url": "/create"
        #} 
]

class User:
    def __init__(self, userID: str):
        #load user from db
        self.userID = userID

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self) -> str:
        return self.userID;

@loginManager.user_loader
def loadUser(user_id):
    return User(user_id)

@app.route("/")
@app.route("/home")
@app.route("/index")
def index():

    return render_template("index.html", menu=menu)

@app.errorhandler(404)
def error_404(error):
     
    return render_template("error_404.html", menu=menu)

@app.route("/login")
def login():

    return render_template("login.html", menu=menu)

if __name__ == "__main__":
    app.run("0.0.0.0", port=4221, debug=app.config.get("DEBUG"))
