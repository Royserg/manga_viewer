from flask import Flask, render_template, jsonify, session

import os
import requests


# ----APP CONFIG----
app = Flask(__name__)

app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'


# ----CUSTOM FILTERS FOR Jinja----
# def reverse_filter(s):
#     return s[::-1]

# app.jinja_env.filters['reverse'] = reverse_filter


# ----ROUTES----
@app.route('/')
def index():
    # get list of Mangas from API https://www.mangaeden.com/api
    r = requests.get('https://www.mangaeden.com/api/list/0/?p=0')
    data = r.json()['manga']
    # print(r.text)

    # pass data into the template
    return render_template('index.html', mangas=data)


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
    app.run(debug=True)
