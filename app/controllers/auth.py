from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from app.models.users import User

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    # If user is already logged in, redirect to book titles
    if current_user.is_authenticated:
        return redirect(url_for('bookController.book_titles'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        
        # Validate input
        if not email or not password or not name:
            flash('All fields are required.', 'danger')
            return render_template('register.html', panel="Register")
        
        # Check if user already exists
        existing_user = User.getUser(email)
        if existing_user:
            flash('Email address already registered.', 'danger')
            return render_template('register.html', panel="Register")
        
        # Create new user
        User.createUser(email=email, name=name, password=password)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', panel="Register")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # If user is already logged in, redirect to book titles
    if current_user.is_authenticated:
        return redirect(url_for('bookController.book_titles'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validate input
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html', panel="Login")
        
        # Find user by email
        user = User.getUser(email)
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user)
            
            # Redirect to next page or book titles
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('bookController.book_titles'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', panel="Login")
    
    return render_template('login.html', panel="Login")


@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('bookController.book_titles'))


# Load the current user if any
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    print('loading user_id:', user_id)
    return User.getUserById(user_id)