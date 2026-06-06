from flask import Flask, g
from db import get_db
from outsideapi.outsideapi import find_city
from web.routes import web
from api.routes import api
import secrets

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)
app.register_blueprint(web)
app.register_blueprint(api, url_prefix='/api')

SETUP = """
CREATE TABLE IF NOT EXISTS cities (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
visited INTEGER NOT NULL DEFAULT 0 CHECK (visited IN (0,1,2)),
added_on TEXT NOT NULL DEFAULT (datetime('now')),
latitude REAL,
longitude REAL,
country TEXT NOT NULL,
population INTEGER,
geonameid INTEGER,
rating INTEGER DEFAULT 0 CHECK (rating BETWEEN 0 AND 10),
rated INTEGER NOT NULL DEFAULT 0 CHECK (rated IN (0,1))
);

CREATE INDEX IF NOT EXISTS idx_cities_visited ON cities(visited);
CREATE INDEX IF NOT EXISTS idx_cities_added_on ON cities(added_on);
"""

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript(SETUP)
    db.commit()

@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("✔ Baza została zainicjowana")

@app.cli.command("seed-db")
def seed_db():
    db = get_db()
    howManyRows = db.execute("SELECT COUNT(*) FROM cities").fetchone()[0]
    if howManyRows == 0:
        db.executemany("INSERT INTO cities(name, country, latitude, longitude, population, geonameid) VALUES (?, ?, ?, ?, ?, ?)",[find_city("Tokyo"), find_city("Kraków"), find_city('New York'), find_city('London'), find_city('Quito'), find_city('Sydney'), find_city('Cairo')])
        db.commit()
        print("✔ Tabela cities została wypełniona przykładowymi danymi")
    else:
        print("❌ Tabela cities zawiera dane, nie wypełniam jej przykładowymi danymi")    


if __name__ == '__main__':
    app.run(debug=True)