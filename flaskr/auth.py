import functools
from urllib import request

from flask import Blueprint, flash
from flask import g as globals
from flask import redirect, render_template, request, session, url_for

from flaskr.database import get_database, sanitizeHTML

blueprint = Blueprint("auth", __name__, url_prefix="/auth")

@blueprint.before_app_request
def load_login():
    id = session.get("user_id")

    if id == None:
        globals.user = None
    else:
        user = get_database().execute("SELECT * FROM user WHERE id = ?", (id,)).fetchone()
        globals.user = {
            "username": user["username"],
            "id": user["id"],
            "timestamp": user["timestamp"]
        }

@blueprint.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_database()
        error = None

        if not username:
            error = "Username field is required."
        elif not password:
            error = "Password field is required."
        elif len(password) < 8:
            error = "Password length must be greater or equal to 8."
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = "A there is already a user with that username."
            else:
                return redirect(url_for("auth.login"), code=307)
        flash(error)
    return render_template("auth/register.html")

@blueprint.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash(request.form["password"])
        db = get_database()
        error = None
        print((username))
        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()

        if user is None:
            error = "That user is not registered."
        elif not username:
            error = "Username field is required."
        elif str(password) != str(user["password"]):
            print(password, user["password"])
            error = "Password is incorrect."
        
        if error is None:
            last_post_timestamp = session.get("last_post_timestamp")
            session.clear()
            session["user_id"] = user["id"]
            session["last_post_timestamp"] = last_post_timestamp
            return redirect(url_for("index"))
        flash(error)
    if session.get("user_id"):
        return redirect(url_for("index"))
    return render_template("auth/login.html")

@blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def require_login(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if globals.user is None:
            flash("You need to be logged in to do that.")
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view
