from flask import Flask, render_template, request, redirect, url_for
from books import all_books

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

def process_book_data(book, index):
    """Convert teacher's book format to our expected format"""
    # Handle multiple authors
    author_str = ", ".join(book['authors']) if isinstance(book['authors'], list) else book['authors']
    
    # Handle genres (use first genre as primary category display)
    genres_str = ", ".join(book['genres']) if isinstance(book['genres'], list) else book['genres']
    
    # Handle description (join list into single string)
    description_str = " ".join(book['description']) if isinstance(book['description'], list) else book['description']
    
    # Create processed book object
    processed_book = {
        'id': str(index + 1),  # Generate ID from index
        'title': book['title'],
        'author': author_str,
        'category': book['category'],
        'genres': genres_str,  # Store full genres string
        'pages': book['pages'],
        'copies': book['copies'],
        'available': book['available'],
        'cover_image': book['url'],  # Map 'url' to 'cover_image'
        'description': description_str,
        'description_list': book['description'],  # Keep original list for paragraph extraction
        'formatted_description': format_full_description(book['description'])  # For details page
    }
    
    return processed_book

def get_book_by_id(book_id):
    """Find a book by its ID"""
    try:
        index = int(book_id) - 1  # Convert to 0-based index
        if 0 <= index < len(all_books):
            return process_book_data(all_books[index], index)
    except (ValueError, IndexError):
        pass
    return None

def get_books_by_category(category=None):
    """Get books filtered by category and sorted alphabetically by title"""
    processed_books = []
    
    # Process all books first
    for index, book in enumerate(all_books):
        processed_book = process_book_data(book, index)
        processed_books.append(processed_book)
    
    # Sort ALL books alphabetically by title
    processed_books.sort(key=lambda x: x['title'].lower())
    
    # Then filter by category if specified
    if category and category.lower() != 'all':
        filtered_books = [book for book in processed_books if book['category'].lower() == category.lower()]
        return filtered_books
    
    return processed_books

def get_first_and_last_paragraphs(description_list):
    """Extract first and last paragraphs from description list for preview"""
    if not description_list or len(description_list) == 0:
        return "No description available for this book."
    
    # If it's a string (fallback), convert to list
    if isinstance(description_list, str):
        # Try to split by double newlines first, then by periods
        paragraphs = [p.strip() for p in description_list.split('\n\n') if p.strip()]
        if len(paragraphs) <= 1:
            paragraphs = [p.strip() for p in description_list.split('. ') if p.strip()]
    else:
        # It's already a list of paragraphs
        paragraphs = [p.strip() for p in description_list if p.strip()]
    
    if len(paragraphs) == 0:
        return "No description available for this book."
    elif len(paragraphs) == 1:
        return paragraphs[0]
    else:
        # Return ONLY first and last paragraphs with spacing
        first = paragraphs[0]
        last = paragraphs[-1]
        return first + "<br><br>" + last

def format_full_description(description_list):
    """Format full description with proper paragraph spacing for details page"""
    if not description_list or len(description_list) == 0:
        return "No description available for this book."
    
    # If it's a string, return as-is
    if isinstance(description_list, str):
        return description_list
    
    # If it's a list, join with double line breaks for paragraph spacing
    paragraphs = [p.strip() for p in description_list if p.strip()]
    return '<br><br>'.join(paragraphs)

# Routes
@app.route('/')
def home():
    return redirect(url_for('book_titles'))

@app.route('/book-titles')
def book_titles():
    """Display all books with optional category filtering"""
    category = request.args.get('category', '').lower()
    books = get_books_by_category(category)
    
    # Prepare books with preview descriptions
    books_with_preview = []
    for book in books:
        book_copy = book.copy()
        # Use the original description list for paragraph extraction
        book_copy['description_preview'] = get_first_and_last_paragraphs(book.get('description_list', book['description']))
        books_with_preview.append(book_copy)
    
    return render_template('book_titles.html', 
                         books=books_with_preview, 
                         selected_category=category)

@app.route('/book-details/<book_id>')
def book_details(book_id):
    """Display detailed information about a specific book"""
    book = get_book_by_id(book_id)
    
    if not book:
        return redirect(url_for('book_titles'))
    
    return render_template('book_details.html', book=book)

@app.errorhandler(404)
def not_found_error(error):
    return redirect(url_for('book_titles'))