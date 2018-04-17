from application import app, db

# set up models
with app.app_context():
    db.create_all()