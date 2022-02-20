from crypt import methods
from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flaskr.auth import require_login
from flaskr.database import get_database

blueprint = Blueprint("dm", __name__, url_prefix="/direct")

@blueprint.route("/recipient/<recipientid>")
@require_login
def view(recipientid):
    db = get_database()
    authorid = session.get("user_id")
    recipient_user = db.execute("SELECT id,username,timestamp FROM user WHERE id = ?", (recipientid,)).fetchone()
    error = None
    
    if recipient_user is None:
        error = "That user is not registered."
    elif str(authorid) == str(recipientid):
        error = "You cannot direct message yourself."
    
    if error is None:
        recipient = {
            "id": recipientid,
            "username": recipient_user["username"],
            "timestamp": recipient_user["timestamp"]
        }
        directmessages = db.execute(
            "SELECT * FROM directmessage WHERE (authorid = ? AND recipientid = ?) OR (authorid = ? AND recipientid = ?)",
            (authorid, recipientid, recipientid, authorid)
        ).fetchall()
        directmessages = [{
            "content": directmessage["content"],
            "author": db.execute("SELECT username FROM user WHERE id = ?", (directmessage["authorid"],)).fetchone()["username"],
            "authorid": directmessage["authorid"],
            "recipient": db.execute("SELECT username FROM user WHERE id = ?", (directmessage["recipientid"],)).fetchone()["username"],
            "recipientid": directmessage["recipientid"],
            "replyingid": directmessage["replyingid"],
            "timestamp": directmessage["timestamp"]
        } for directmessage in directmessages]
        return render_template("user/direct.html", recipient=recipient, directmessages=directmessages)
    flash(error)
    return redirect(url_for("index"))

@blueprint.route("/send/<recipientid>", methods=("POST",))
@require_login
def send(recipientid):
    db = get_database()
    content = request.form["content"]
    authorid = session.get("user_id")
    recipient = db.execute("SELECT username FROM user WHERE id = ?", (recipientid,)).fetchone()
    error = None

    if content is None:
        error = "Direct message content field is required."
        print("NoContentError")
    elif recipient is None:
        error = "Attempted to send direct message to non-existent user."
        flash(error)
        print("RecipientNotExistError")
        return redirect(url_for("index"))
    
    if error is None:
        db.execute(
            "INSERT INTO directmessage(content, authorid, recipientid, replyingid) VALUES (?, ?, ?, ?)",
            (content, authorid, recipientid, None)
        )
        db.commit()
    else:
        flash(error)
    return redirect(url_for("dm.view", recipientid=recipientid))