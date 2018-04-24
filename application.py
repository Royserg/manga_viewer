import os
import requests
import datetime

from flask import Flask, render_template, jsonify, session, request, url_for, redirect
from flask_session import Session
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
    """Show index page - Manga Search"""
    # init server-side session
    if session.get('mangas') is None:
        session['mangas'] = {}

    return render_template('index.html')


# ---PULL SUGGESTIONS FROM DB---
@app.route('/api/suggestions')
def suggestions():
    """Fetch 5 picks from database matching query and return them"""
    query = request.args.get('query')
    
    # query db for 10 matches
    data = Manga.query.filter(Manga.alias.like(f"{query}%")).limit(5).all()
    
    # transform data from db into JSON
    suggestions = {}

    for manga in data:
        suggestions[manga.title] = {
                                    "image": manga.image, # for possible implementation of dropdown divs
                                    "last_date": datetime.datetime.fromtimestamp(int(manga.last_chap_date)).strftime('%d-%m-%Y')
                                    }
    
    return jsonify(suggestions)


@app.route('/manga/<manga_alias>/')
def about_manga(manga_alias):
    """Query db for id of chosen manga, gather all info about manga from API and display"""

    manga_id = Manga.query.filter_by(alias=f'{manga_alias}').first().id
    print(f"=====Manga id: {manga_id}====")
    
    # init chapters storage for manga title in session
    if session['mangas'].get(manga_alias) is None:
        session['mangas'][manga_alias] = {}
    
    # get info about manga from API https://www.mangaeden.com/api/manga/[manga.id]/
    r = requests.get(f'https://www.mangaeden.com/api/manga/{manga_id}')
    data = r.json()
    chapters = data['chapters']
    
    # test
    print(f'from API, length: {len(chapters)}')

    # put mangas id's into session for manga alias
    if len(session['mangas'][manga_alias]) == 0:
        for chapter in chapters:
            session['mangas'][manga_alias][chapter[0]] = chapter[3]

    # testing
    length = len(session['mangas'][manga_alias])
    print(f"{manga_alias}== {length}")
    return render_template('about_manga.html', manga=data)


@app.route('/manga/<alias>/<int:chapter>')
def chapter(alias, chapter):
    # retrieve chapter id from the session
    try:
        chapter_id = session['mangas'].get(alias)[chapter]
    except KeyError:
        # Flash msg: Couldn't find Chapter
        return redirect(url_for('about_manga', manga_alias=alias))
    except TypeError:
        # Flash msg: Filled session, choose the chapter again
        return redirect(url_for('about_manga', manga_alias=alias))

    print(f'========chapter_id: {chapter_id}==========')
    # pull chapter Data from API
    # r = requests.get('https://www.mangaeden.com/api/chapter/5372443e45b9ef33a85f0ffb')
    r = requests.get(f'https://www.mangaeden.com/api/chapter/{chapter_id}')

    r_pages = r.json()['images']
    # manga images are in descending order, reverse them
    pages = []
    for page in r_pages:
        pages.insert(0, page)

    return render_template('chapter.html', pages=pages, chapter=chapter, alias=alias)


if __name__ == '__main__':    
    # seed data from API if table is empty
    with app.app_context():
        if not Manga.query.all():
            print("seeding data to db")
            init_db()
    
    app.secret_key = os.urandom(24)
    app.config['SESSION_TYPE'] = 'filesystem'

    Session(app)
    app.run(debug=True)

    