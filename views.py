import requests
import datetime

from application import app
from flask import render_template, jsonify, session, request, url_for, redirect
from flask_session import Session
from models import Manga, User

# ----CUSTOM FILTERS----
@app.template_filter('timestamp_to_time')
def timestamp_to_time(timestamp, format):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime(format)


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
    # get argument from input
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
    """Query db for id of chosen manga, gather all info about manga from API and display them"""

    try:
        manga_id = Manga.query.filter_by(alias=f'{manga_alias}').first().id
        print(f"=====Manga id: {manga_id}====")
    except AttributeError:
        # Flash msg: Couldn't find that Manga
        return redirect(url_for('index'))
    
    # init chapters storage for manga title in session
    if session['mangas'].get(manga_alias) is None:
        session['mangas'][manga_alias] = {}
    
    # get info about manga from API https://www.mangaeden.com/api/manga/[manga.id]/
    r = requests.get(f'https://www.mangaeden.com/api/manga/{manga_id}')
    data = r.json()
    chapters = data['chapters']
    
    # test
    session_length = len(session['mangas'][manga_alias])
    print(f'from API, length: {len(chapters)}')
    print(f"{manga_alias}== {session_length}")

    # put mangas id's into session for manga alias
    if session_length == 0 or session_length != len(chapters):
        for chapter in chapters:
            session['mangas'][manga_alias][chapter[0]] = chapter[3]

        
    return render_template('about_manga.html', manga=data)

# TODO: Fix url converter so it doesn't show XX.0 as a chapter number
@app.route('/manga/<alias>/<float:chapter>')
def chapter(alias, chapter):
    """Show Manga chapter images one under another"""
    # retrieve chapter id from the session
    try:
        chapter_id = session['mangas'].get(alias)[chapter]
        title = Manga.query.filter_by(alias=alias).first().title
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

    return render_template('chapter.html', pages=pages, chapter=chapter, alias=alias, title=title)
