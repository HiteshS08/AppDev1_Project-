from application.models import User, Playlist, Song, PlaylistSong, Creator
from flask import current_app as app
from application.database import db
from main import login_manager
from flask import Flask, render_template, redirect, url_for, flash, request, session, send_from_directory
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, logout_user
from sqlalchemy import or_
import os

UPLOAD_FOLDER = 'static'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def start():
    return render_template('index.html')

@app.route("/<id>")
def default(id):
    user = User.query.filter_by(id = id).first()
    return render_template("index.html", user = user)

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user.disabled == False:
            if user and user.pwd == password:
                if user.id is not None:  
                    login_user(user)
                    return redirect(url_for('home', id=user.id))
                else:
                    flash('Invalid User ID', 'danger')
                    return redirect(url_for('user_login'))
            else:
                flash('Login failed. Please check your username and password', 'danger')
                return redirect(url_for('user_login'))  
        
        else:
            flash("Your Account has been disabled", "danger")
        
    return render_template('user_login.html')

@app.route('/admin_login', methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()

        if user.identity != "Admin":
            flash('Admin Authentication Failed', 'danger')
            return redirect(url_for('admin_login'))

        if user and user.pwd == password:
            login_user(user)
            return redirect(url_for('home', id=user.id))

    return render_template('admin_login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect('/')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mail = request.form.get('mail')
        user = User(username = username, pwd = password, mail = mail)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_login'))
    return render_template('register.html')

@app.route('/home/<int:id>')
@login_required
def home(id = None):
    if id is not None:
        playlists = Playlist.query.filter_by(user_id = id).all()
    else:
        playlists = Playlist.query.filter_by(user_id = current_user.id).all()

    songs = Song.query.all()
    return render_template('home.html',User = current_user, id = current_user.id, songs=songs, playlists=playlists)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/playlist/<int:playlist_id>')
def playlist(playlist_id):
    playlist = Playlist.query.filter_by(id = playlist_id).first()
    if playlist:
        playlistSongs = playlist.songs
        songs = []
        for playlistSong in playlistSongs:
            song = Song.query.filter_by(sid = playlistSong.id).first()
            songs.append(song)
        print(songs)
        
        return render_template('playlist.html',User = current_user, playlist=playlist, songs=songs)
    else:
        flash('Playlist not found', 'danger')
        return redirect(url_for('home', id = current_user.id))


@app.route('/<int:playlist_id>/add_song', methods=['GET', 'POST'])
def add_song(playlist_id):
    songs = Song.query.all()
    playlist = Playlist.query.filter_by(id = playlist_id).first()

    if request.method == 'POST':
        song_id = request.form.get('song_id')
        if song_id:
            new_song = PlaylistSong(playlist_id = playlist_id, song_id = song_id)
            db.session.add(new_song)
            db.session.commit()
        else:
            flash('Song ID is Invalid', 'error')
            redirect(url_for('add_song', playlist_id = playlist_id))
        
        return redirect(url_for('playlist', playlist_id = playlist.id))
    
    return render_template('add_song.html', songs = songs, User = current_user, playlist = playlist)


@app.route('/<int:playlist_id>/remove_song', methods=['GET', 'POST'])
@login_required
def remove_song(playlist_id):
    playlist = Playlist.query.filter_by(id = playlist_id).first()
    songs = Song.query.all()

    if request.method == 'POST':
        song_id = request.form.get('song_id')
        playlist_song = PlaylistSong.query.filter_by(playlist_id = playlist_id, song_id = song_id).first()
        if playlist_song:
            db.session.delete(playlist_song)
            db.session.commit()
            flash('Song deleted successfully!', 'success')
            redirect(url_for('playlist', id = current_user.id))
        else:
            flash('Song not found in the playlist', 'danger')
            return redirect(url_for('remove_song', playlist_id = playlist_id))

        return redirect(url_for('playlist', playlist_id = playlist.id))
    
    return render_template('remove_song.html', songs = songs, User = current_user, playlist = playlist)

@app.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    songs = Song.query.all()
    playlist_created = False
    playlist_name = None

    if request.method == 'POST':
        user_id = current_user.id
        playlist_name =  request.form.get('playlist_name')
        song_id = request.form.get('song_id')

        if not playlist_name:
            flash('Playlist name is required.', 'error')
            return redirect(url_for('create_playlist'))
        
        
        playlist = Playlist.query.filter_by(name=playlist_name, user_id = user_id).first()

        

        if not playlist:
            playlist = Playlist(name=playlist_name, user_id = user_id)
            db.session.add(playlist)
            db.session.commit()
            playlist_created = True

        if song_id:
            playlist_song = PlaylistSong(playlist_id = playlist.id, song_id = song_id)
            db.session.add(playlist_song)
            db.session.commit()

        
    return render_template("create_playlist.html", songs=songs, playlist_created=playlist_created, playlist_name=playlist_name)


@app.route('/delete_playlist/<int:playlist_id>')
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id = playlist_id).first()
    if playlist:
        db.session.delete(playlist)
        db.session.commit()
        db.session.refresh(playlist)
    else:
        flash('Playlist not found', 'danger')

    return redirect(url_for('home', id=current_user.id))


@app.route('/lyrics/<int:song_id>')
def get_lyrics(song_id):
    song = Song.query.filter_by(sid = song_id)
    name = song.sname
    filename = f"{name}.txt"
    return send_from_directory('static/lyrics', filename)

    
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


@app.route('/creator_register/<int:id>', methods = ['GET', 'POST'])
def creator_registor(id):
    user = User.query.get(id)
    if request.method == "POST":
        if user.pwd == request.form.get('password'):
            cname = request.form.get('creator_name')
            creator = Creator(cname = cname, user_id = user.id)
            db.session.add(creator)
            db.session.commit()
            return redirect(url_for('creator', id = user.id))

        
        
    
    creator = Creator.query.filter_by(user_id = user.id).first()
    if creator:
        return redirect(url_for('creator', id = creator.user_id))
    
    
    
    cname = request.form.get('creator_name')
    password = request.form.get('password')

    

    return render_template('creator_register.html', user = current_user, id = current_user.id)

@app.route('/<int:id>/creator', methods = ['GET', 'POST'])
@login_required
def creator(id):
    creator = Creator.query.get(id)
    songs = Song.query.filter_by(cname = creator.cname , flagged = False).all()
    flagged_songs = Song.query.filter_by(cname = creator.cname, flagged = True).all()
    return render_template('creator.html', songs = songs, flagged_songs = flagged_songs)


@app.route('/upload_song', methods = ['GET','POST'])
def upload_song():
    if request.method == "GET":

        return render_template('upload_song.html')
    
    if request.method == "POST":
        user = User.query.filter_by(id = current_user.id).first()
        cname = user.username
        

        song_name = request.form.get('song_name')
        song_lyrics = request.form.get('song_lyrics')
        song_image = request.files['song_image']
       

        

        lyrics_path = os.path.join('static', 'lyrics', f'{song_name}.txt')
        with open(lyrics_path, 'w') as lyrics_file:
            lyrics_file.write(song_lyrics)

        if song_image.filename != "":
            image_path = os.path.join('static', f'{song_name}.jpg')
            song_image.save(image_path)
            return redirect("/creator")
        else:
            flash("Invalid file", 'error')
            return redirect(url_for('upload_song'))

        