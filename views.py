import requests
import datetime

from application import app
from flask import render_template, jsonify, session, request, url_for, redirect, flash
from flask_session import Session
from flask_login import login_user, login_required, logout_user, current_user
from models import *
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash


# ----CUSTOM FILTERS----
@app.template_filter('timestamp_to_time')
def timestamp_to_time(timestamp, format):
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime(format)


# ----ROUTES----
@app.route('/')
@app.route('/manga')
@login_required
def index():
    """Show index page - Manga Search"""
    # init server-side session
    if session.get('mangas') is None:
        session['mangas'] = {}

    subs = []

    for manga in current_user.subscriptions:
        r = requests.get(f'https://www.mangaeden.com/api/manga/{manga.id}')
        data = r.json()
        subs.append(
            {
                "title": data["title"],
                "alias": data["alias"],
                "image": f"https://cdn.mangaeden.com/mangasimg/{data['image']}",
                "last_chapter_date": data["last_chapter_date"],
            }
        )
    

    return render_template('index.html', subs=subs)


# ----LOGOUT----
@app.route('/logout')
@login_required
def logout():
    """Logout User"""
    logout_user()
    flash("You successfully logged out", 'success')
    return redirect(url_for('login'))


# ----REGISTER----
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Dispaly Registration Form for creating new account"""
    form = RegisterForm()

    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data.lower()
        user_exists = User.query.filter_by(username=username).first()
        # if that username already exists show error msg
        if user_exists:
            flash("That username is already taken, try different one", 'danger')
            return redirect(url_for('register'))

        # create new user when username is not taken
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(
                        username=username,
                        email=form.email.data,
                        password=hashed_password
                    )

        db.session.add(new_user)
        db.session.commit()

        flash('You have been registered, please log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


# ----LOGIN----
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Form"""
    form = LoginForm()

    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user:
            # provided password for that user is okay, log in user, redirect to index
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash(f'Welcome, {user.username}', 'success')
                return redirect(url_for('index'))
        # if username or password was not correct
        flash('Invalid username or password', 'danger')
        return redirect(url_for('login'))
    
    return render_template('login.html', form=form)


# ----API----
# ---PULL SUGGESTIONS FROM DB---
@app.route('/api/suggestions')
@login_required
def suggestions():
    """Fetch 5 picks from database matching query and return them"""
    # get argument from input
    query = request.args.get('query')

    # query db for 10 matches
    data = Manga.query.filter(Manga.alias.like(f"{query}%")).limit(5).all()
    
    # transform data from db into JSON
    suggestions = {}
    # ===========================
    # keep image info and last date for possible implementing of dropdown with img
    # ===========================
    for manga in data:
        suggestions[manga.title] = {
                                    "image": manga.image,
                                    "last_date": datetime.datetime.fromtimestamp(int(manga.last_chap_date)).strftime('%d-%m-%Y')
                                    }
    
    return jsonify(suggestions)


# ----SUBSCRIBE----
@app.route('/api/subscribe', methods=['POST'])
@login_required
def subscribe():
    """Save manga into favorites, so it will display on the main page"""
    # retrieve data from request
    data = request.get_json()
    manga_id = data.get('manga_id')

    # insert directly into helper table
    sub = subs.insert().values(user_id=current_user.id, manga_id=manga_id)
    db.session.execute(sub)
    db.session.commit()

    return "subscribed"

# ----UNSUBSCRIBE----
@app.route('/api/unsubscribe', methods=['POST'])
@login_required
def unsubscribe():
    """Delete manga from favorites"""
    # retrieve data from request
    data = request.get_json()
    manga_id = data.get('manga_id')
    
    # delete row from association table
    del_sub = subs.delete().where(
            subs.c.user_id == current_user.id).where(
            subs.c.manga_id == manga_id)

    db.session.execute(del_sub)
    db.session.commit()

    return "unsubscribed"

@app.route('/manga/<manga_alias>/')
@login_required
def about_manga(manga_alias):
    """Query db for id of chosen manga, gather all info about manga from API and display them"""

    try:
        manga_id = Manga.query.filter_by(alias=f'{manga_alias}').first().id
    except AttributeError:
        flash("Couldn't find that Manga", 'danger')
        return redirect(url_for('index'))
    
    # Check if subscribed
    subscribed = False
    for manga in current_user.subscriptions:
        if manga.id == manga_id:
            subscribed = True

    # init chapters storage for manga title in session
    if session['mangas'].get(manga_alias) is None:
        session['mangas'][manga_alias] = {}
    
    # get info about manga from API https://www.mangaeden.com/api/manga/[manga.id]/
    r = requests.get(f'https://www.mangaeden.com/api/manga/{manga_id}')
    data = r.json()
    chapters = data['chapters']
    
    session_length = len(session['mangas'][manga_alias])
    # put mangas id's into session for manga alias
    if session_length == 0 or session_length != len(chapters):
        for chapter in chapters:
            # store chapter number in session as a string - key
            chap_number = str(chapter[0])
            session['mangas'][manga_alias][chap_number] = chapter[3]
    
    return render_template('about_manga.html', manga=data, subscribed=subscribed, manga_id=manga_id)


@app.route('/manga/<alias>/<chapter>')
@login_required
def chapter(alias, chapter):
    """Show Manga chapter images one under another"""
    # retrieve chapter id from the session
    try:
        chapter_id = session['mangas'].get(alias)[chapter]
        # get title of selected manga
        title = Manga.query.filter_by(alias=alias).first().title
    except KeyError:
        flash("Couldn't find Chapter", "danger")
        return redirect(url_for('about_manga', manga_alias=alias))
    except TypeError:
        flash("Filled session, choose the chapter again", "info")
        return redirect(url_for('about_manga', manga_alias=alias))

    # pull chapter Data from API
    r = requests.get(f'https://www.mangaeden.com/api/chapter/{chapter_id}')

    r_pages = r.json()['images']
    # manga images are in descending order, reverse them
    pages = []
    for page in r_pages:
        pages.insert(0, page)
    
    # prepare object for chapters navigation buttons
    chapter_nav = {
        "current": chapter,
        "previous": None,
        "next": None
    }

    # get list of chapter numbers from session object
    chapter_numbers = list(session['mangas'][alias].keys())[::-1]    
    # loop over list of chapter numbers and find selected chapter, get previous and next one
    for i in range(len(chapter_numbers)):
        if chapter_numbers[i] == chapter:
            # When current chapter is 0, `previous` is becoming the last - fix
            try:
                if i is 0:
                    prev_chapter = None
                else:
                    prev_chapter = chapter_numbers[i-1]
            except IndexError:
                prev_chapter = None
            
            try:
                next_chapter = chapter_numbers[i+1]
            except IndexError:
                next_chapter = None

            chapter_nav["previous"] = prev_chapter
            chapter_nav["next"] = next_chapter

    return render_template('chapter.html', pages=pages, chapter_nav=chapter_nav, alias=alias, title=title)
