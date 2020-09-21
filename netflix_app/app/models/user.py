from .core import db

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(64), nullable=False, primary_key=True)
    lastname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    created_on = db.Column(db.DateTime(True), nullable=False, default=db.func.now())

