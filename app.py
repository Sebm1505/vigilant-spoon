from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps

# Import app, db, and login_manager from __init__
from app import app, db, login_manager

# Import controllers (Blueprints)
from app.controllers.auth import auth
from app.controllers.bookController import book

# Import models
from app.models.book import Book
from app.models.users import User

# Import initial book data
from books import all_books

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(book)

# Initialize Book collection and default users on startup
with app.app_context():
    Book.initialize_collection(all_books)

    # Initialize default users if they don't exist
    if User.objects.count() == 0:
        # Create admin user
        admin = User(
            email='admin@lib.sg',
            name='Admin',
            is_admin=True
        )
        admin.set_password('12345')
        admin.save()
        
        # Create regular user
        user = User(
            email='poh@lib.sg',
            name='Peter Oh',
            is_admin=False
        )
        user.set_password('12345')
        user.save()
        
        print("Default users created successfully.")

if __name__ == '__main__':
    app.run(debug=True)