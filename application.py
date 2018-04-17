import os
import requests
import datetime

from flask import Flask, render_template, jsonify, session, request
from models import *

# ----APP CONFIG----
app = Flask(__name__)

POSTGRES = {
    'user': 'postgres',
    'pw': 'N1ezn0ny',
    'db': 'manga_viewer',
    'host': 'localhost',
    'port' : '5432',
}

# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://nkjxsufzdqjwve:bc3b21d99aa07f8ce33024fe8449e1d88a10afb7be9dba390cfc739f711ba0e4@ec2-54-75-244-248.eu-west-1.compute.amazonaws.com:5432/ddse5bgkj7mct3'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
db.init_app(app)

# ----INITIAL DATA SEED----
def init_db():
    # Manga API https://www.mangaeden.com/api
    r = requests.get('https://www.mangaeden.com/api/list/0')
    data = r.json()['manga']
    for manga in data:
        if "ld" in manga:
            m = Manga(id=manga["i"], alias=manga["a"], title=manga["t"], image=manga["im"], last_chap_date=manga.get("ld"))
            db.session.add(m)
    db.session.commit()

# ----ROUTES----
@app.route('/')
def index():
    # query database for mangas information
    data = Manga.query.all()
    
    return render_template('index.html', mangas=data)


@app.route('/api/suggestions/<q>')
def suggestions(q):
    """Fetch 10 picks from database matching query and return them"""
    
    # transform query for querying by alias [ex. boku-no-hero]
    query = "-".join(q.lower().split(" "))
    
    # query db for 10 matches
    data = Manga.query.filter(Manga.alias.like(f"{query}%")).limit(10).all()
    
    # transform data from db into JSON
    suggestions = {}

    for manga in data:
        suggestions[manga.title] = {
                                    "id": manga.id,
                                    "image": manga.image,
                                    "last_date": datetime.datetime.fromtimestamp(int(manga.last_chap_date)).strftime('%d-%m-%Y')
                                    }
    
    return jsonify(suggestions)


@app.route('/<manga_title>')
def manga(manga_title):
    # query the db to find proper manga ID
    r = requests.get('https://www.mangaeden.com/api/manga/5aa9b638719a1652eae2652d')
    data = r.json()

    # pull informations from json
    title = data['title']
    chapters = data['chapters']

    # initialize title session if doesn't exist
    if session.get('title') is None:
        session['title'] = ""

    # initialize chapters session if doesn't exist
    if session.get('chapters') is None:
        session['chapters'] = []

    # save into session
    session['title'] = title

    return render_template('about_manga.html', title=title, chapters=chapters)


@app.route('/<manga_title>/<int:chapter>')
def chapter(manga_title, chapter):
    # pull chapter from API
    r = requests.get('https://www.mangaeden.com/api/chapter/4e711cb0c09225616d037cc2')
    r_pages = r.json()['images']
    # pages of chapter are in the descending order, below reversing them
    pages = []
    for page in r_pages:
        pages.insert(0, page)

    return render_template('chapter.html', pages=pages, chapter=chapter)


if __name__ == '__main__':
    
    # seed data from API if table is empty
    with app.app_context():
        if not Manga.query.all():
            print("seeding data to db")
            init_db()

    app.run(debug=True)
    
    
    # initialy fill all of the titles to the db
    
    
