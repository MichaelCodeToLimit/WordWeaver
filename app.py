import os
import logging
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # Generate a secure key
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # We'll enable it explicitly where needed
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable time limit for development

# Configure the database
# Use SQLite for development
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wordweaver.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Enable CSRF protection globally
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = app.secret_key
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow CSRF token without HTTPS

# Initialize Socket.IO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize extensions
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)

# Configure login
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    try:
        from models import User
        return User.query.get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {str(e)}")
        return None

@app.route('/ping')
def ping():
    """Test endpoint to verify app is running"""
    return jsonify({"status": "ok"})

# Initialize the application
with app.app_context():
    # Import models first
    import models  # noqa: F401
    logger.info("Models imported")

    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

    # Register blueprints after database is ready
    from auth import auth as auth_blueprint
    from routes import main as main_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    logger.info("Blueprints registered successfully")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)