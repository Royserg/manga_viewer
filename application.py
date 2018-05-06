from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from models import *

# ----APP INIT----
app = Flask(__name__)
app.config.from_pyfile('config.py')
Session(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


# ----Login Manager loader-----
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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

# import all views
from views import *

if __name__ == '__main__':    
    # seed data from API if table is empty
    with app.app_context():
        if not Manga.query.all():
            print("seeding data to db")
            init_db()

    app.run()
