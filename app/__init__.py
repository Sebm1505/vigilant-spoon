from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    
    # MongoDB Configuration
    app.config['MONGODB_SETTINGS'] = {
        'db': 'library_db',
        'host': 'localhost',
        'port': 27017
    }
    
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Initialize MongoEngine
    db = MongoEngine(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login or register first to access this page."
    
    return app, db, login_manager

app, db, login_manager = create_app()