import sqlite3

import click
from flask import Flask, current_app
from flask import g as globals
from flask.cli import with_appcontext

def sanitizeHTML(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def init(app: Flask):
    app.teardown_appcontext(close_database)
    app.cli.add_command(reset_db)

def get_database():
    if "db" not in globals:
        globals.db = sqlite3.connect(current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        globals.db.row_factory = sqlite3.Row
    return globals.db

def close_database(_ = None):
    db: sqlite3.Connection = globals.pop("db", None)
    if db is not None:
        db.close()

@click.command("reset-db")
@with_appcontext
def reset_db():
    click.echo("Resetting DBs...")
    db = get_database()
    with current_app.open_resource("sqlite3/schema.sql") as sql:
        db.executescript(sql.read().decode("utf8"))
