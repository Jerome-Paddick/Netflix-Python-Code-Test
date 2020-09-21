from .core import db
from sqlalchemy.orm import relationship

class Shows(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)
    year = db.Column(db.String(32), nullable=False)
    released = db.Column(db.DateTime, nullable=False)
    plot = db.Column(db.String(256), nullable=False)
    imdb_rating = db.Column(db.Float(), nullable=False)
    seasons = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(16), nullable=False)
    updated_on = db.Column(db.DateTime, nullable=False, default=db.func.now())
    episodes = relationship('Episodes')

class Episodes(db.Model):
    __tablename__ = 'episodes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.ForeignKey('shows.id', ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(64), nullable=False)
    plot = db.Column(db.String(256), nullable=False)
    year = db.Column(db.String(32), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    episode = db.Column(db.Integer, nullable=False)
    released = db.Column(db.DateTime, nullable=False)
    imdb_rating = db.Column(db.Float(), nullable=False)
    language = db.Column(db.String(16), nullable=False)
    updated_on = db.Column(db.DateTime, nullable=False, default=db.func.now())
    comments = relationship('EpisodeComments')

class EpisodeComments(db.Model):
    __tablename__ = 'episode_comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    episode_id = db.Column(db.ForeignKey('episodes.id', ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=db.func.now())