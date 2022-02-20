import json
from math import floor
import time, datetime
from flask import Blueprint, Response, render_template, request, redirect, session, url_for, flash

from flaskr.auth import require_login;
from flaskr.database import get_database, sanitizeHTML

blueprint = Blueprint("post", __name__, url_prefix="/p")
    
@blueprint.route("/create", methods=("GET", "POST"))
@require_login
def create():
    if session.get("last_post_timestamp"):
        if (session.get("last_post_timestamp") + (1 * 60)) > time.time():
            dsec = (session.get("last_post_timestamp") + (1 * 60)) - time.time()
            sec = floor(dsec % 60)
            min = floor(dsec / 60)
            if True:
                flash(f"Please wait {str(min)}m {str(sec)}s before creating another post.")
                return redirect(url_for("index"))
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = session.get("user_id")
        error = None

        if title is None:
            error = "Title field is required."
        elif content is None:
            error = "Content field is required."
        
        if error is None:
            db = get_database()
            db.execute(
                "INSERT INTO post(authorid, title, content) VALUES (?, ?, ?)",
                (author, title, content)
            )
            db.commit()
            postid = db.execute(
                "SELECT id FROM post WHERE authorid = ? AND title = ?",
                (author, title)
            ).fetchone()
            session["last_post_timestamp"] = time.time()
            return redirect(url_for("post.view", postid=postid["id"]))
        flash(error)
    return render_template("post/create.html")

@blueprint.route("/postcomment/<postid>", methods=("POST",))
@require_login
def comment(postid):
    db = get_database()
    content = request.form["content"]
    authorid = session.get("user_id")
    error = None

    if content is None:
        error = "Content field is required."

    if error is None:
        print(content)
        db.execute(
            "INSERT INTO comment(postid, authorid, replyingid, content) VALUES (?, ?, ?, ?)",
            (postid, authorid, None, content)
        )
        db.commit()
    else:
        flash(error)
    
    return redirect(url_for("post.view", postid=postid))

@blueprint.route("/replycomment/<commentid>", methods=("POST",))
@require_login
def replycomment(commentid):
    db = get_database()
    comment = db.execute("SELECT * FROM comment WHERE id = ?", (commentid,)).fetchone()
    content = request.form["content"]
    authorid = session.get("user_id")
    postid = comment["postid"]
    error = None

    if comment is None:
        error = "Comment doesn't exist."
    elif content is None:
        error = "Content reply field is required."

    if error is None:
        db.execute(
            "INSERT INTO comment(postid, authorid, replyingid, content) VALUES (?, ?, ?, ?)",
            (postid, authorid, commentid, content)
        )
        db.commit()
    else:
        flash(error)
    
    return redirect(url_for("post.view", postid=postid))

@blueprint.route("/fetchreplies/<commentid>", methods=("POST",))
def fetchreplies(commentid):
    db = get_database()
    comment = db.execute("SELECT * FROM comment WHERE id = ?", (commentid,)).fetchone()
    error = None

    if comment is None:
        error = "Comment doesn't exist."
        return Response(json.dumps({"code": 400, "message": error}), status=400, mimetype="application/json")
    else:
        replies = [{
            "id": comment["id"],
            "authorid": comment["authorid"],
            "author": db.execute("SELECT username FROM user WHERE id = ?", (comment["authorid"],)).fetchone()["username"],
            "content": comment["content"],
            "timestamp": comment["timestamp"]
        } for comment in db.execute("SELECT * FROM comment WHERE replyingid = ?", (commentid,)).fetchall()]
        return Response(json.dumps({"code": 200, "body": replies}), status=200, mimetype="application/json")

@blueprint.route("/view/<postid>", methods=("GET",))
def view(postid):
    user_id = session.get("user_id")
    db = get_database()
    post = db.execute("SELECT * FROM post WHERE id = ?", (postid,)).fetchone()
    user_comments = [{
        "content": comment["content"],
        "timestamp": comment["timestamp"],
        "id": comment["id"]
    } for comment in db.execute("SELECT content,timestamp,id FROM comment WHERE postid = ? AND authorid = ? AND replyingid IS NULL ORDER BY id DESC", (postid, user_id,)).fetchall()]

    other_comments = [{
        "content": comment["content"],
        "authorid": comment["authorid"],
        "timestamp": comment["timestamp"],
        "id": comment["id"],
        "author": db.execute("SELECT username FROM user WHERE id = ?", (comment["authorid"],)).fetchone()["username"]
    } for comment in db.execute("SELECT content,authorid,timestamp,id FROM comment WHERE postid = ? AND authorid != ? AND replyingid IS NULL ORDER BY id DESC", (postid, user_id,)).fetchall()]
    if post is None:
        flash("That post does not exist.")
        return redirect(url_for("index"))
    authorName = db.execute("SELECT username FROM user WHERE id = ?", (post["authorid"],)).fetchone()
    return render_template("post/view.html", post={
        "id": post["id"],
        "authorid": post["authorid"],
        "title": post["title"],
        "content": post["content"],
        "timestamp": post["timestamp"],
        "author": authorName["username"],
        "comments": {
            "user": user_comments,
            "other": other_comments
        }
    })