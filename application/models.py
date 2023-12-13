from flask_login import UserMixin
from .database import db

class User(UserMixin, db.Model):    
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    mail = db.Column(db.String, unique=True, nullable=False)
    pwd = db.Column(db.String, nullable=False)
    identity = db.Column(db.String, nullable=False, default="User", server_default="User")
    disabled = db.Column(db.Boolean, default=False, nullable=False) 
    playlists = db.relationship('Playlist', backref='user', lazy=True)

    def is_active(self):
        return self.active

class Creator(db.Model):
    __tablename__ = "Creator"
    id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True, nullable=False)
    cname = db.Column(db.String, unique=True, nullable=False)
    disabled = db.Column(db.Boolean, default=False, nullable=False) 
    songs = db.relationship('Song', backref='creator', lazy=True)

class Song(db.Model):
    __tablename__ = "Song"
    sid = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    sname = db.Column(db.String, unique=True, nullable=False)
    cname = db.Column(db.String, db.ForeignKey('Creator.cname'), nullable=False)
    flagged = db.Column(db.Boolean, default=False, nullable=False)
    playlists = db.relationship('PlaylistSong', back_populates='song', cascade='all, delete-orphan')

class Playlist(db.Model):
    __tablename__ = "Playlist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    songs = db.relationship('PlaylistSong', back_populates='playlist', cascade='all, delete-orphan')

class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('Playlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('Song.sid'), nullable=False)
    playlist = db.relationship('Playlist', back_populates='songs')
    song = db.relationship('Song', back_populates='playlists')

class Album(db.Model):
    __tablename__ = "Album"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    cname = db.Column(db.String, db.ForeignKey('Creator.cname'), nullable=False)
    flagged = db.Column(db.Boolean, default=False, nullable=False)

db.create_all()


 