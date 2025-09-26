"""
Flask E-Library Application - Question 2(b)
Implementation with MongoDB integration, user authentication, and Book class
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
from books import all_books
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# MongoDB Configuration
MONGO_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.elibrary_db

# Collections
books_collection = db.books
users_collection = db.users

class Book:
    """
    Book class representing a book document in MongoDB
    Based on the class diagram requirements for Q2(b)
    """
    
    def __init__(self, title, author, category, isbn, publication_year, publisher, cover_image, description, _id=None):
        self._id = _id
        self.title = title
        self.author = author
        self.category = category
        self.isbn = isbn
        self.publication_year = publication_year
        self.publisher = publisher
        self.cover_image = cover_image
        self.description = description
    
    @classmethod
    def initialize_collection(cls):
        """
        Initialize the Book collection in MongoDB.
        If collection is empty, populate with data from all_books variable.
        """
        # Check if collection is empty
        if books_collection.count_documents({}) == 0:
            print("Book collection is empty. Initializing with sample data...")
            
            # Create Book documents from all_books data
            for book_data in all_books:
                book = cls(
                    title=book_data['title'],
                    author=book_data['author'],
                    category=book_data['category'],
                    isbn=book_data['isbn'],
                    publication_year=book_data['publication_year'],
                    publisher=book_data['publisher'],
                    cover_image=book_data['cover_image'],
                    description=book_data['description']
                )
                book.save()
            
            print(f"Successfully initialized {len(all_books)} books in MongoDB collection.")
        else:
            print(f"Book collection already contains {books_collection.count_documents({})} documents.")
    
    def save(self):
        """Save the book to MongoDB collection"""
        book_doc = {
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'isbn': self.isbn,
            'publication_year': self.publication_year,
            'publisher': self.publisher,
            'cover_image': self.cover_image,
            'description': self.description,
            'created_at': datetime.utcnow()
        }
        
        if self._id:
            books_collection.update_one({'_id': self._id}, {'$set': book_doc})
        else:
            result = books_collection.insert_one(book_doc)
            self._id = result.inserted_id
        
        return self._id
    
    @classmethod
    def find_all(cls, category=None, sort_by='title'):
        """
        Find all books, optionally filtered by category
        Returns list of Book objects sorted by specified field
        """
        query = {}
        if category and category.lower() != 'all':
            query['category'] = {'$regex': f'^{category}$', '$options': 'i'}
        
        # MongoDB query with sorting
        cursor = books_collection.find(query).sort(sort_by, 1)
        
        books = []
        for doc in cursor:
            book = cls(
                title=doc['title'],
                author=doc['author'],
                category=doc['category'],
                isbn=doc['isbn'],
                publication_year=doc['publication_year'],
                publisher=doc['publisher'],
                cover_image=doc['cover_image'],
                description=doc['description'],
                _id=doc['_id']
            )
            books.append(book)
        
        return books
    
    @classmethod
    def find_by_id(cls, book_id):
        """Find a book by its MongoDB ObjectId"""
        try:
            doc = books_collection.find_one({'_id': ObjectId(book_id)})
            if doc:
                return cls(
                    title=doc['title'],
                    author=doc['author'],
                    category=doc['category'],
                    isbn=doc['isbn'],
                    publication_year=doc['publication_year'],
                    publisher=doc['publisher'],
                    cover_image=doc['cover_image'],
                    description=doc['description'],
                    _id=doc['_id']
                )
        except Exception as e:
            print(f"Error finding book by ID {book_id}: {e}")
        return None
    
    def to_dict(self):
        """Convert Book object to dictionary for template rendering"""
        return {
            'id': str(self._id),
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'isbn': self.isbn,
            'publication_year': self.publication_year,
            'publisher': self.publisher,
            'cover_image': self.cover_image,
            'description': self.description
        }

class User:
    """User class for authentication management"""
    
    def __init__(self, email, name, password_hash, is_admin=False, _id=None):
        self._id = _id
        self.email = email
        self.name = name
        self.password_hash = password_hash
        self.is_admin = is_admin
    
    @classmethod
    def initialize_admin_users(cls):
        """Initialize default admin and user accounts"""
        # Create admin user if doesn't exist
        if not users_collection.find_one({'email': 'admin@lib.sg'}):
            admin_user = cls(
                email='admin@lib.sg',
                name='Admin',
                password_hash=generate_password_hash('12345'),
                is_admin=True
            )
            admin_user.save()
            print("Admin user created: admin@lib.sg")
        
        # Create regular user if doesn't exist
        if not users_collection.find_one({'email': 'poh@lib.sg'}):
            regular_user = cls(
                email='poh@lib.sg',
                name='Peter Oh',
                password_hash=generate_password_hash('12345'),
                is_admin=False
            )
            regular_user.save()
            print("Regular user created: poh@lib.sg")
    
    def save(self):
        """Save user to MongoDB"""
        user_doc = {
            'email': self.email,
            'name': self.name,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'created_at': datetime.utcnow()
        }
        
        if self._id:
            users_collection.update_one({'_id': self._id}, {'$set': user_doc})
        else:
            result = users_collection.insert_one(user_doc)
            self._id = result.inserted_id
        
        return self._id
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email address"""
        doc = users_collection.find_one({'email': email})
        if doc:
            return cls(
                email=doc['email'],
                name=doc['name'],
                password_hash=doc['password_hash'],
                is_admin=doc.get('is_admin', False),
                _id=doc['_id']
            )
        return None
    
    def check_password(self, password):
        """Check if provided password matches user's password"""
        return check_password_hash(self.password_hash, password)

# WTForms for user authentication
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# Initialize database collections on app startup
@app.before_first_request
def initialize_database():
    """Initialize MongoDB collections with sample data"""
    Book.initialize_collection()
    User.initialize_admin_users()

# Helper function to check if user is logged in
def is_logged_in():
    return 'user_id' in session

def get_current_user():
    """Get current logged-in user"""
    if is_logged_in():
        return users_collection.find_one({'_id': ObjectId(session['user_id'])})
    return None

# Routes
@app.route('/')
def home():
    return redirect(url_for('book_titles'))

@app.route('/book-titles')
def book_titles():
    """
    CHANGE FROM Q2(a): Now uses Book.find_all() method to query MongoDB
    instead of directly using all_books variable
    """
    category = request.args.get('category', '').lower()
    
    # Use Book class method to fetch from MongoDB
    books = Book.find_all(category=category)
    
    # Convert Book objects to dictionaries for template
    books_data = [book.to_dict() for book in books]
    
    current_user = get_current_user()
    
    return render_template('book_titles.html', 
                         books=books_data, 
                         selected_category=category,
                         current_user=current_user,
                         is_logged_in=is_logged_in())

@app.route('/book-details/<book_id>')
def book_details(book_id):
    """
    CHANGE FROM Q2(a): Now uses Book.find_by_id() method to query MongoDB
    Uses ObjectId instead of integer ID
    """
    # Use Book class method to fetch from MongoDB
    book = Book.find_by_id(book_id)
    
    if not book:
        flash('Book not found.', 'error')
        return redirect(url_for('book_titles'))
    
    current_user = get_current_user()
    
    return render_template('book_details.html', 
                         book=book.to_dict(),
                         current_user=current_user,
                         is_logged_in=is_logged_in())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if is_logged_in():
        return redirect(url_for('book_titles'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        
        if user and user.check_password(form.password.data):
            session['user_id'] = str(user._id)
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin
            
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('book_titles'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if is_logged_in():
        return redirect(url_for('book_titles'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.find_by_email(form.email.data)
        if existing_user:
            flash('Email address already registered.', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password_hash=generate_password_hash(form.password.data),
            is_admin=False
        )
        new_user.save()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    """User logout route"""
    user_name = session.get('user_name', 'User')
    session.clear()
    flash(f'Goodbye, {user_name}!', 'info')
    return redirect(url_for('book_titles'))