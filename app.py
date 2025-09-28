from flask import Flask, render_template, request, redirect, url_for, flash
from books import all_books

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'


@app.route('/')
def home():
    return redirect(url_for('book_titles'))


@app.route('/book-titles')
def book_titles():
    """Display list of books, optionally filtered by category"""
    category = request.args.get('category', '').lower()

    if category and category != 'all':
        books = [b for b in all_books if b['category'].lower() == category]
    else:
        books = all_books

    return render_template('book_titles.html',
                           books=books,
                           selected_category=category)


@app.route('/book-details/<int:book_id>')
def book_details(book_id):
    """Display details for a single book"""
    book = next((b for b in all_books if b['id'] == book_id), None)
    if not book:
        flash('Book not found.', 'error')
        return redirect(url_for('book_titles'))

    return render_template('book_details.html', book=book)