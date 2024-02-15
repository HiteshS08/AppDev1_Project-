from flask import Flask, render_template, request, redirect, url_for, make_response, session
from flask import current_app as app
from application.models import User, Playlist, Song, PlaylistSong, Creator, Album, AlbumSong
from .database import db
import secrets 
from flask_restful import Resource, Api,fields,marshal_with
from flask import make_response, jsonify
from flask_restful import reqparse 
from werkzeug .exceptions import HTTPException
import json
app.secret_key = secrets.token_hex()
class NotFoundError(HTTPException):
    def __init__(self,status_code):
        self.response = make_response('',status_code)
class BuisnessValidationError(HTTPException):
    def __init__(self,status_code,error_code,error_message):
        message = {'error_code':error_code,'error_message':error_message}
        self.response = make_response(json.dumps(message),status_code)


output_fields = {"id": fields.Integer,"username": fields.String,"mail":fields.String}
class SignupAPI(Resource):
    @marshal_with(output_fields)
    def get(self,user_id):
        user = db.session.query(User).filter(User.id== user_id).first()
        if user:
            return user
        else:
            raise NotFoundError(status_code=404)
        
output_fields = {"name": fields.String, "user_id": fields.Integer}
class PlaylistAPI(Resource):
    @marshal_with(output_fields)
    def get(self, id):
        playlist = db.session.query(Playlist).filter(Playlist.id == id).first()
        if playlist:
            return playlist
        else:
            raise NotFoundError(status_code=404)


output_fields = {"name": fields.String, "user_id": fields.Integer, "cname": fields.String, "flagged": fields.Boolean}
class AlbumAPI(Resource):
    @marshal_with(output_fields)
    def get(self, id):
        album = db.session.query(Album).filter(Album.id == id).first()
        if album:
            return album
        else:
            raise NotFoundError(status_code=404)
        

output_fields = {"sname": fields.String, "cname": fields.String, "flagged": fields.Boolean, "lyrics": fields.String}
class SongAPI(Resource):
    @marshal_with(output_fields)
    def get(self, sid):
        song = db.session.query(Song).filter(Song.sid == sid).first()
        if song:
            return song
        else:
            raise NotFoundError(status_code=404)
        

output_fields = {"user_id": fields.Integer, "cname": fields.String, "disabled": fields.Boolean}
class CreatorAPI(Resource):
    @marshal_with(output_fields)
    def get(self, id):
        creator = db.session.query(Creator).filter(Creator.id == id).first()
        if creator:
            return creator
        else:
            raise NotFoundError(status_code=404)