from flask import Flask, render_template, request, redirect, url_for
from models import Book
from mongoengine import connect

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

# Initialize Book collection on startup
with app.app_context():
    Book.initialize_collection()

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

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors by redirecting to book titles."""
    return redirect(url_for('book_titles'))