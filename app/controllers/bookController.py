from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.models.book import Book

book = Blueprint('bookController', __name__)


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('bookController.book_titles'))
        return f(*args, **kwargs)
    return decorated_function


@book.route('/')
@book.route('/book-titles')
def book_titles():
    """Display all books with optional category filtering."""
    category = request.args.get('category', '').lower()
    
    # Get books from MongoDB
    books_query = Book.get_all_books_sorted(category)
    
    # Convert Book documents to dictionaries for template
    books = [book.to_dict() for book in books_query]
    
    return render_template('book_titles.html', 
                         books=books, 
                         selected_category=category,
                         panel="Book Titles")


@book.route('/book-details/<book_id>')
def book_details(book_id):
    """Display detailed information about a specific book."""
    # Get book from MongoDB by ID
    book_doc = Book.get_book_by_id(book_id)
    
    if not book_doc:
        # If book not found, redirect to book titles
        return redirect(url_for('bookController.book_titles'))
    
    # Convert to dictionary for template
    book_dict = book_doc.to_dict()
    
    return render_template('book_details.html', book=book_dict, panel="Book Details")


@book.route('/new-book', methods=['GET', 'POST'])
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
            return render_template('new_book.html', genres=genres, panel="Add a Book")
        
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
            return render_template('new_book.html', genres=genres, panel="Add a Book")
        
        # Process description into paragraphs
        description_paragraphs = [p.strip() for p in description.replace('\r\n', '\n').split('\n\n') if p.strip()]
        if not description_paragraphs:
            description_paragraphs = [description]
        
        try:
            # Create new book
            Book.createBook(
                genres=selected_genres,
                title=title,
                category=category,
                url=url,
                description=description_paragraphs,
                authors=authors,
                pages=pages,
                copies=copies
            )
            
            flash(f'Book "{title}" has been successfully added to the library!', 'success')
            return redirect(url_for('bookController.new_book'))
            
        except Exception as e:
            flash(f'An error occurred while adding the book: {str(e)}', 'danger')
            return render_template('new_book.html', genres=genres, panel="Add a Book")
    
    return render_template('new_book.html', genres=genres, panel="Add a Book")


@book.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors by redirecting to book titles."""
    return redirect(url_for('bookController.book_titles'))