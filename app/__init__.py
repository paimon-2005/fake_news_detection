from flask import Flask
from flask_cors import CORS
from app.models import db
from config import Config

def create_app():
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    
    from app.routes import api, main
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
        
    return app
