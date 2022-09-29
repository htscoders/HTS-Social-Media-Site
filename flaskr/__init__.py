# https://flask.palletsprojects.com/en/2.0.x/

import os

from flask import Flask, render_template
from flaskr.database import get_database


def app_factory():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = os.getenv("PRIVATE_KEY"),
        DATABASE = os.path.join(app.instance_path, "database.sqlite")
    )

    try:
        os.makedirs(app.instance_path)
    except FileExistsError:
        pass

    @app.route("/")
    def index():
        db = get_database()
        recent_posts = db.execute("SELECT id,authorid,title,timestamp FROM post ORDER BY id DESC").fetchall()
        recent_posts = [{
            "id": post["id"],
            "authorid": post["authorid"],
            "title": post["title"],
            "timestamp": post["timestamp"],
            "author": db.execute("SELECT username FROM user WHERE id = ?", (post["authorid"],)).fetchone()["username"]
        } for post in recent_posts]
        return render_template("app/index.html", recent_posts=recent_posts)
    
    # Modules
    from . import database
    database.init(app)

    # Blueprints
    from . import auth
    app.register_blueprint(auth.blueprint)

    from . import post
    app.register_blueprint(post.blueprint)

    from . import user
    app.register_blueprint(user.blueprint)

    from . import directmessage
    app.register_blueprint(directmessage.blueprint)
    
    return app
