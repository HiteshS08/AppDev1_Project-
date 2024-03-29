import os
from flask import Flask
from flask_restful import Api
from application.config import LocalDevelopmentConfig
from application.database import db

from flask_login import LoginManager



app = None
api = None
def create_app():
    
    app = Flask(__name__)
    app.secret_key = 'yf4f38g34fyb348f'
    if os.getenv("ENV","development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api

app, api = create_app()
login_manager = LoginManager(app)

from application.controllers import *
from application.API import *
api.add_resource(SignupAPI,"/api/signup/<user_id>")
api.add_resource(PlaylistAPI, "/api/playlist/<id>")
api.add_resource(AlbumAPI, "/api/album/<id>")
api.add_resource(SongAPI, "/api/song/<sid>")
api.add_resource(CreatorAPI, "/api/creator/<id>")

if __name__ == "__main__":
    app.run(
        debug = True
    )

