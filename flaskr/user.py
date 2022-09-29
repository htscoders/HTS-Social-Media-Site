from flask import Blueprint, flash, redirect, render_template, url_for
from flaskr.database import get_database
blueprint = Blueprint("user", __name__, url_prefix="/u")

@blueprint.route("/<userid>", methods=("GET",))
def view(userid):
    db = get_database()
    
    user = db.execute(
        "SELECT * FROM user WHERE id = ?",
        (userid,)
    ).fetchone()
    
    posts = db.execute(
        "SELECT id,title,timestamp FROM post WHERE authorid = ? ORDER BY id DESC",
        (userid,)
    ).fetchall()

    if user is None:
        flash("That user does not exist.")
        return redirect(url_for("index"))
    
    if posts is None:
        posts = []
    else:
        posts = [{
            "id": post["id"],
            "title": post["title"],
            "timestamp": post["timestamp"]
        } for post in posts]
    
    return render_template("user/view.html", user={
        "username": user["username"],
        "id": userid,
        "timestamp": user["timestamp"],
        "posts": posts
    })