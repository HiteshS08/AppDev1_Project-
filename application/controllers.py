from application.models import User, Playlist, Song, PlaylistSong
from flask import current_app as app
from application.database import db
from main import login_manager
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import or_

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def start():
    return redirect(url_for('login'))

@app.route("/<id>")
def default(id):
    user = User.query.filter_by(id = id).first()
    return render_template("index.html", user = user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.pwd == password:
            if user.id is not None:  
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('home', id=user.id))
            else:
                flash('User ID is not valid.', 'danger')
        else:
            flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mail = request.form.get('mail')
        user = User(username = username, pwd = password, mail = mail)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/home/<int:id>')
@login_required
def home(id = None):
    if id is not None:
        playlists = Playlist.query.filter_by(user=id).all()
    else:
        playlists = Playlist.query.filter_by(user=current_user.id).all()

    songs = Song.query.all()
    return render_template('home.html',User = current_user, id = current_user.id, songs=songs, playlists=playlists)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/playlist/<int:playlist_id>')
def view_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        songs = playlist.songs
        return render_template('playlist.html',User = current_user, playlist=playlist, songs=songs)
    else:
        flash('Playlist not found', 'danger')
        return redirect(url_for('home'))


@app.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    songs = Song.query.all()
    playlist_created = False
    playlist_name = None

    if request.method == 'POST':
        playlist_name =  request.form.get('playlist_name')
        user_id = current_user.id
        playlist = Playlist.query.filter_by(name=playlist_name, user=user_id).first()

        if not playlist:
            playlist = Playlist(name=playlist_name, user=user_id)
            db.session.add(playlist)
            db.session.commit()

        playlist_created = True

    return render_template("create_playlist.html", songs=songs,User = current_user, playlist_created=playlist_created, playlist_name=playlist_name)


@app.route('/add_song/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def add_song(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    songs = Song.query.all()
    playlist_updated = False

    if request.method == 'POST':
        song_id = request.form.get("song_id")
        song = Song.query.get(song_id)

        if song not in playlist.songs:
            playlist.songs.append(song)
            db.session.commit()
            playlist_updated = True
    return redirect(url_for('create_playlist'))

    
@app.route('/search')
def search():
    query = request.args.get('q')
    songs = Song.query.filter(
        or_(
            Song.sname.ilike(f"%{query}%"),
            Song.cname.ilike(f"%{query}%"),
        )
    ).all()
    return render_template('search.html', songs = songs, User = current_user, id = current_user.id)