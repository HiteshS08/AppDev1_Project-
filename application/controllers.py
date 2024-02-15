from application.models import User, Playlist, Song, PlaylistSong, Creator, Album, AlbumSong
from flask import current_app as app
from application.database import db
from main import login_manager
from flask import Flask, render_template, redirect, url_for, flash, request, session, send_from_directory
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, logout_user
from sqlalchemy import or_, and_
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
            return redirect(url_for('user_login'))
        
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
            return redirect('/admin')

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

    songs = (
        Song.query
        .join(Creator, Song.cname == Creator.cname)
        .filter(and_(Creator.disabled == False, Song.flagged == False))
        .all()
    )
    albums = (
        Album.query
        .join(Creator, Album.cname == Creator.cname)
        .filter(Creator.disabled == False)
        .all()
    )
    return render_template('home.html',User = current_user, id = current_user.id, songs=songs, playlists=playlists, albums = albums)


@app.route('/playlist/<int:playlist_id>')
def playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id).first()

    if playlist:
        playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist.id).all()
        songs = []
        for playlist_song in playlist_songs:
            song = Song.query.join(Creator).filter(
                Song.sid == playlist_song.song_id,
                Song.flagged == False,
                Creator.disabled == False
            ).first()
            if song:
                songs.append(song)

        return render_template('playlist.html', User=current_user, playlist=playlist, songs=songs)
    else:
        return redirect(url_for('home', id=current_user.id))



@app.route('/<int:playlist_id>/add_song', methods=['GET', 'POST'])
def add_song(playlist_id):
    songs = (
        Song.query
        .join(Creator, Song.cname == Creator.cname)
        .filter(and_(Creator.disabled == False, Song.flagged == False))
        .all()
    )
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
    songs = (
        Song.query
        .join(Creator, Song.cname == Creator.cname)
        .filter(and_(Creator.disabled == False, Song.flagged == False))
        .all()
    )

    if request.method == 'POST':
        song_id = request.form.get('song_id')
        playlist_song = PlaylistSong.query.filter_by(playlist_id = playlist_id, song_id = song_id).first()
        if playlist_song.song_id in [song.song_id for song in playlist.songs]:
            db.session.delete(playlist_song)
            db.session.commit()
            return redirect(url_for('playlist', playlist_id=current_user.id))
        else:
            return redirect(url_for('remove_song', playlist_id=playlist_id))
    
    return render_template('remove_song.html', songs = songs, User = current_user, playlist = playlist)

@app.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    songs = (
        Song.query
        .join(Creator, Song.cname == Creator.cname)
        .filter(and_(Creator.disabled == False, Song.flagged == False))
        .all()
    )
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
    else:
        flash('Playlist not found', 'danger')

    return redirect(url_for('home', id=current_user.id))


@app.route('/search')
def search():
    query = request.args.get('q')
    songs = Song.query.filter(
        and_(
            or_(
                Song.sname.ilike(f"%{query}%"),
                Song.cname.ilike(f"%{query}%"),
            ),
            Song.flagged == False
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

@app.route('/creator/<int:id>', methods = ['GET', 'POST'])
@login_required
def creator(id):
    creator = Creator.query.filter_by(user_id = id).first()
    if creator.disabled == False:
        songs = Song.query.filter_by(cname = creator.cname , flagged = False).all()
        flagged_songs = Song.query.filter_by(cname = creator.cname, flagged = True).all()
        albums = Album.query.filter_by(cname = creator.cname).all()
    else:
        flash("You have been whitelisted", "danger")
        return redirect(url_for('home', id = current_user.id))
    return render_template('creator.html', songs = songs, flagged_songs = flagged_songs, albums = albums)


@app.route('/upload_song', methods = ['GET','POST'])
def upload_song():
    if request.method == "GET":
        return render_template('upload_song.html')
    
    if request.method == "POST":
        user = User.query.filter_by(id = current_user.id).first()
        cname = user.username
        song_name = request.form.get('song_name')
        lyrics = request.form.get('song_lyrics')
        song_image = request.files['song_image']
        song_file = request.files['song_file']

        if song_image.filename != "" and song_file.filename != "":

            if song_file.filename.endswith('.mp3'):
                song_filename = f"{song_name}.mp3"
                song_file.save(os.path.join('static', 'music', song_filename))
                image_path = os.path.join('static', f'{song_name}.jpg')
                song_image.save(image_path)
                song = Song(sname = song_name, cname = cname, lyrics = lyrics)
                db.session.add(song)
                db.session.commit()
                return redirect(f"/creator/{current_user.id}")
            else:
                flash("Invalid file format. Please upload an MP3 file.", 'error')
                return redirect(url_for('upload_song'))
        else:
            flash("Invalid file", 'error')
            return redirect(url_for('upload_song'))
        
@app.route('/play/<int:song_id>')
def play(song_id):
    song = Song.query.get(song_id)
    if song:
        return render_template('play_song.html', song=song)
    else:
        flash('Song not found', 'danger')
        return redirect(url_for('home', id=current_user.id))
    
@app.route('/delete_song/<int:id>', methods = ['GET','POST'])
def delete_song(id):
    song_id = request.form.get('song_id')
    creator = Creator.query.filter_by(user_id = current_user.id).first()
    songs = Song.query.filter_by(cname = creator.cname).all()
    if request.method == "POST":
        song = Song.query.filter_by(sid = song_id).first()
        if song.cname == creator.cname:
            db.session.delete(song)
            db.session.commit()
            return redirect(f'/creator/{current_user.id}')
        else:
            return redirect(f'/delete_song/{current_user.id}')
    return render_template('delete_song.html', songs = songs)


@app.route('/create_album', methods=['GET', 'POST'])
@login_required
def create_album():
    creator = Creator.query.filter_by(user_id = current_user.id).first()
    songs = Song.query.filter_by(cname = creator.cname, flagged = False).all()
    album_created = False
    album_name = None

    if request.method == 'POST':
        user_id = current_user.id
        album_name = request.form.get('album_name')
        song_id = request.form.get('song_id')

        if not album_name:
            return redirect(url_for(create_album))
        
        album = Album.query.filter_by(name=album_name, user_id=user_id).first()

        if not album:
            album = Album(name=album_name, user_id=user_id, cname = creator.cname)
            db.session.add(album)
            db.session.commit()
            album_created = True    

        if song_id:
            album_song = AlbumSong(album_id=album.id, song_id=song_id)
            db.session.add(album_song)
            db.session.commit()
            return redirect(f"/creator/{current_user.id}")

    return render_template("create_album.html", songs=songs, album_created=album_created, album_name=album_name)


@app.route('/album/<int:album_id>')
def album(album_id):
    album = Album.query.filter_by(id = album_id).first()
    
    if album:
        albumsongs= album.album_songs
        songs = []
        for i in albumsongs:
            albumsong = AlbumSong.query.filter_by(id = i.id).first()
            song = Song.query.filter_by(sid = albumsong.song_id, flagged = False).first()
            
            songs.append(song)
        print(songs)
        
        return render_template('album.html',User = current_user, album = album, songs=songs)
    else:
        return redirect(url_for('home', id = current_user.id))


@app.route('/delete_album', methods = ["GET", "POST"])
@login_required
def delete_album():

    creator = Creator.query.filter_by(user_id = current_user.id).first()
    album_id = request.form.get('album_id')
    albums = Album.query.filter_by(cname = creator.cname)
    album = Album.query.filter_by(id = album_id).first()
    print(album)
    if album:
        db.session.delete(album)
        db.session.commit()
        return redirect(url_for('creator', id = current_user.id))
    return render_template('delete_album.html', albums = albums)


@app.route('/admin', methods = ["GET", "POST"])
@login_required
def admin_dashboard():
    songs = Song.query.all()
    users = User.query.filter_by(identity = "User").all()
    creators = Creator.query.all()
    total_users = db.session.query(User).count()
    total_creators = db.session.query(Creator).count()
    total_songs = db.session.query(Song).count()

    return render_template('admin_dashboard.html', songs=songs, users = users, creators = creators, total_users = total_users, total_songs = total_songs, total_creators = total_creators)

@app.route('/flag_song/<int:song_id>')
@login_required
def flag_song(song_id):
    song = Song.query.get(song_id)
    if song:
        song.flagged = not song.flagged
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/whitelist_creator/<int:creator_id>', methods = ["GET", "POST"])
@login_required
def whitelist_creator(creator_id):
    creator = Creator.query.filter_by(id = creator_id).first()
    if creator:
        creator.disabled = not creator.disabled
        db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/flag_user/<int:id>', methods = ["GET", "POST"])
@login_required
def flag_user(id):
    user = User.query.filter_by(id = id).first()
    if user:
        user.disabled = not user.disabled
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

