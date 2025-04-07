from flask import Flask, render_template, redirect, g

from SETTINGS import web_app_secret_key, web_app_debug

app = Flask("ruinKeeper")
app.config.update(SECRET_KEY=web_app_secret_key)
app.config.update(DEBUG=web_app_debug)

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
        {
            "title": "Запись",
            "url": "/create"
        } 
]

@app.route("/")
@app.route("/home")
@app.route("/index")
def index():

    return render_template("index.html", menu=menu)

if __name__ == "__main__":
    app.run("0.0.0.0", port=4221, debug=app.config.get("DEBUG"))
