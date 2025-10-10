from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import random
from app.models.book import Book
from app.models.loan import Loan

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


@book.route('/make-loan/<book_id>', methods=['GET', 'POST'])
@login_required
def make_loan(book_id):
    """Handle making a loan for a book."""
    # Get the book
    book_doc = Book.get_book_by_id(book_id)
    
    if not book_doc:
        flash('Book not found.', 'danger')
        return redirect(url_for('bookController.book_titles'))
    
    # Check if user is admin - admins cannot make loans
    if current_user.is_admin:
        flash('Admin users cannot make loans.', 'danger')
        return redirect(url_for('bookController.book_details', book_id=book_id))
    
    if request.method == 'POST':
        # Generate random borrow date (10-20 days before today)
        days_ago = random.randint(10, 20)
        borrow_date = datetime.now() - timedelta(days=days_ago)
        
        # Create the loan
        success, message, loan = Loan.create_loan(current_user, book_doc, borrow_date)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('bookController.my_loans'))
        else:
            flash(message, 'danger')
            return redirect(url_for('bookController.book_details', book_id=book_id))
    
    # GET request - show confirmation page
    book_dict = book_doc.to_dict()
    return render_template('make_loan.html', book=book_dict, panel="Make a Loan")


@book.route('/my-loans')
@login_required
def my_loans():
    """Display all loans for the current user."""
    # Get active and returned loans
    active_loans = Loan.get_user_active_loans(current_user)
    returned_loans = Loan.get_user_returned_loans(current_user)
    
    # Convert to dictionaries for template
    active_loans_dict = [loan.to_dict() for loan in active_loans]
    returned_loans_dict = [loan.to_dict() for loan in returned_loans]
    
    return render_template('my_loans.html', 
                         active_loans=active_loans_dict,
                         returned_loans=returned_loans_dict,
                         panel="Current Loans")


@book.route('/renew-loan/<loan_id>')
@login_required
def renew_loan(loan_id):
    """Renew a loan."""
    loan = Loan.get_loan_by_id(loan_id)
    
    if not loan:
        flash('Loan not found.', 'danger')
        return redirect(url_for('bookController.my_loans'))
    
    # Verify loan belongs to current user
    if str(loan.member.id) != str(current_user.id):
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('bookController.my_loans'))
    
    new_borrow_date = datetime.now()
    
    # Update the loan manually
    if loan.returnDate is not None:
        flash("Cannot renew a loan that has already been returned.", 'danger')
        return redirect(url_for('bookController.my_loans'))
    
    MAX_RENEWALS = 2  # Changed from 3 to 2 to match requirement
    if loan.renewCount >= MAX_RENEWALS:
        flash(f"Maximum renewal limit ({MAX_RENEWALS}) reached for '{loan.book.title}'.", 'danger')
        return redirect(url_for('bookController.my_loans'))
    
    loan.renewCount += 1
    loan.borrowDate = new_borrow_date
    loan.save()
    
    flash(f"Successfully renewed '{loan.book.title}'.", 'success')
    return redirect(url_for('bookController.my_loans'))


@book.route('/return-loan/<loan_id>')
@login_required
def return_loan(loan_id):
    """Return a loan."""
    loan = Loan.get_loan_by_id(loan_id)
    
    if not loan:
        flash('Loan not found.', 'danger')
        return redirect(url_for('bookController.my_loans'))
    
    # Verify loan belongs to current user
    if str(loan.member.id) != str(current_user.id):
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('bookController.my_loans'))
    
    return_date = datetime.now()
    
    # Return the loan with the generated date
    success, message = loan.return_loan(return_date)
    flash(message, 'success' if success else 'danger')
    
    return redirect(url_for('bookController.my_loans'))


@book.route('/delete-loan/<loan_id>')
@login_required
def delete_loan(loan_id):
    """Delete a returned loan."""
    loan = Loan.get_loan_by_id(loan_id)
    
    if not loan:
        flash('Loan not found.', 'danger')
        return redirect(url_for('bookController.my_loans'))
    
    # Verify loan belongs to current user
    if str(loan.member.id) != str(current_user.id):
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('bookController.my_loans'))
    
    # Delete the loan
    success, message = loan.delete_loan()
    flash(message, 'success' if success else 'danger')
    
    return redirect(url_for('bookController.my_loans'))


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