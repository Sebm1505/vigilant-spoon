from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Document):
    """User model for authentication and authorization."""
    
    meta = {'collection': 'users'}
    
    email = db.StringField(required=True, unique=True, max_length=100)
    password_hash = db.StringField(required=True)
    name = db.StringField(required=True, max_length=100)
    is_admin = db.BooleanField(default=False)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def getUser(email):
        """Get a user by email address."""
        return User.objects(email=email.lower()).first()
    
    @staticmethod
    def getUserById(user_id):
        """Get a user by their ID."""
        return User.objects(pk=user_id).first()
    
    @staticmethod
    def createUser(email, name, password):
        """Create a new user."""
        user = User.getUser(email)
        if not user:
            user = User(email=email.lower(), name=name, is_admin=False)
            user.set_password(password)
            user.save()
        return user
    
    def __str__(self):
        """String representation of User."""
        return f"{self.name} ({self.email})"