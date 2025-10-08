from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Book, User
from mongoengine import connect
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# MongoDB Configuration
app.config['MONGODB_SETTINGS'] = {
    'db': 'library_db',
    'host': 'localhost',
    'port': 27017
}

# Connect to MongoDB
connect(db='library_db',host='localhost',port=27017)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('book_titles'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize Book collection on startup
with app.app_context():
    Book.initialize_collection()

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

# Routes
@app.route('/')
def home():
    return redirect(url_for('book_titles'))

@app.route('/book-titles')
def book_titles():
    """Display all books with optional category filtering"""
    category = request.args.get('category', '').lower()
    
    # Get books from MongoDB using the Book model
    books_query = Book.get_all_books_sorted(category)
    
    # Convert Book documents to dictionaries for template
    books = [book.to_dict() for book in books_query]
    
    return render_template('book_titles.html', 
                         books=books, 
                         selected_category=category)

@app.route('/book-details/<book_id>')
def book_details(book_id):
    """
    Display detailed information about a specific book.
    
    Args:
        book_id (str): MongoDB ObjectId of the book
    """
    # Get book from MongoDB by ID
    book_doc = Book.get_book_by_id(book_id)
    
    if not book_doc:
        # If book not found, redirect to book titles
        return redirect(url_for('book_titles'))
    
    # Convert to dictionary for template
    book = book_doc.to_dict()
    
    return render_template('book_details.html', book=book)

@app.route('/new-book', methods=['GET', 'POST'])
@login_required
@admin_required
def new_book():
    """Handle adding a new book (admin only)."""
    # List of genres for the form
    genres = ["Animals", "Business", "Comics", "Communication", "Dark Academia", 
              "Emotion", "Fantasy", "Fiction", "Friendship", "Graphic Novels", 
              "Grief", "Historical Fiction", "Indigenous", "Inspirational", "Magic", 
              "Mental Health", "Nonfiction", "Personal Development", "Philosophy", 
              "Picture Books", "Poetry", "Productivity", "Psychology", "Romance", 
              "School", "Self Help"]
    
    if request.method == 'POST':
        # Get form data
        selected_genres = request.form.getlist('genres')
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        url = request.form.get('url', '').strip()
        description = request.form.get('description', '').strip()
        pages = request.form.get('pages', type=int)
        copies = request.form.get('copies', type=int)
        
        # Validate required fields
        if not all([selected_genres, title, category, url, description, pages, copies]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('new_book.html', genres=genres)
        
        # Process authors (up to 5)
        authors = []
        for i in range(1, 6):
            author_name = request.form.get(f'author{i}', '').strip()
            is_illustrator = request.form.get(f'illustrator{i}') == 'yes'
            
            if author_name:
                if is_illustrator:
                    authors.append(f"{author_name} (Illustrator)")
                else:
                    authors.append(author_name)
        
        # Validate at least one author
        if not authors:
            flash('Please provide at least one author.', 'danger')
            return render_template('new_book.html', genres=genres)
        
        # Process description into paragraphs
        # Split by double line breaks or double newlines
        description_paragraphs = [p.strip() for p in description.replace('\r\n', '\n').split('\n\n') if p.strip()]
        if not description_paragraphs:
            description_paragraphs = [description]
        
        try:
            # Create new book
            new_book = Book(
                genres=selected_genres,
                title=title,
                category=category,
                url=url,
                description=description_paragraphs,
                authors=authors,
                pages=pages,
                available=copies,  # Initially all copies are available
                copies=copies
            )
            new_book.save()
            
            flash(f'Book "{title}" has been successfully added to the library!', 'success')
            return redirect(url_for('new_book'))
            
        except Exception as e:
            flash(f'An error occurred while adding the book: {str(e)}', 'danger')
            return render_template('new_book.html', genres=genres)
    
    return render_template('new_book.html', genres=genres)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    # If user is already logged in, redirect to book titles
    if current_user.is_authenticated:
        return redirect(url_for('book_titles'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        
        # Validate input
        if not email or not password or not name:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Email address already registered.', 'danger')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            email=email,
            name=name,
            is_admin=False
        )
        new_user.set_password(password)
        new_user.save()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # If user is already logged in, redirect to book titles
    if current_user.is_authenticated:
        return redirect(url_for('book_titles'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validate input
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')
        
        # Find user by email
        user = User.get_by_email(email)
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user)
            
            # Redirect to next page or book titles
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('book_titles'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('book_titles'))


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors by redirecting to book titles."""
    return redirect(url_for('book_titles'))