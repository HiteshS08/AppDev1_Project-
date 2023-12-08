from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .database import db
from sqlalchemy.sql import expression

class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    username = db.Column(db.String, unique = True, nullable = False)
    mail = db.Column(db.String, unique = True, nullable = False)
    pwd = db.Column(db.String, nullable = False)
    identity = db.Column(db.String, nullable = False, default = "User", server_default = "User")
    active = db.Column(db.Boolean, server_default = expression.true(), nullable = False)

    def is_active(self):
        return self.active

class Creator(db.Model):
    __tablename__ = "Creator"
    id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key = True, nullable = False)
    sid = db.Column(db.Integer, db.ForeignKey('Song.sid'), nullable = False)
    sname = db.Column(db.String, db.ForeignKey('Song.sname'), nullable = False)
    cname = db.Column(db.String, db.ForeignKey('Song.cname'))

class Song(db.Model):
    __tablename__ = "Song"
    sid = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    sname = db.Column(db.String, unique = True, nullable = False)
    cname = db.Column(db.String, unique = True, nullable = False)
    playlists = db.relationship('Playlist', secondary='playlist_song', back_populates='songs')


class Playlist(db.Model):
    __tablename__ = "Playlist"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    name = db.Column(db.String, nullable = False)
    user = db.Column(db.Integer, db.ForeignKey('User.id'), nullable = False)
    songs = db.relationship('Song', secondary='playlist_song', back_populates='playlists')


class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('Playlist.id'))
    song_id = db.Column(db.Integer, db.ForeignKey('Song.sid'))


class Album(db.Model):
    __tablename__ = "Album"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    name = db.Column(db.String, nullable = False)
    cname = db.Column(db.String, db.ForeignKey('Creator.cname'))

class Lyrics(db.Model):
    __tablename__ = "Lyrics"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    words = db.Column(db.String, nullable = False)
    song_id = db.Column(db.Integer, db.ForeignKey('Song.sid'), nullable = False)


db.create_all()