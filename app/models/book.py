from app import db


class Book(db.Document):
    """Book model for library catalog."""
    
    meta = {
        'collection': 'books',
        'ordering': ['title']
    }
    
    genres = db.ListField(db.StringField(), required=True)
    title = db.StringField(required=True, max_length=200)
    category = db.StringField(required=True, max_length=50)
    url = db.StringField(required=True)  # Cover image URL
    description = db.ListField(db.StringField(), required=True)
    authors = db.ListField(db.StringField(), required=True)
    pages = db.IntField(required=True)
    available = db.IntField(required=True, min_value=0)
    copies = db.IntField(required=True, min_value=0)
    
    @staticmethod
    def initialize_collection(all_books):
        """Initialize the Book collection from all_books data."""
        if Book.objects.count() == 0:
            print("Book collection is empty. Initializing from all_books data...")
            
            for book_data in all_books:
                book = Book(
                    genres=book_data['genres'],
                    title=book_data['title'],
                    category=book_data['category'],
                    url=book_data['url'],
                    description=book_data['description'],
                    authors=book_data['authors'],
                    pages=book_data['pages'],
                    available=book_data['available'],
                    copies=book_data['copies']
                )
                book.save()
            
            print(f"Successfully initialized {Book.objects.count()} books in the database.")
        else:
            print(f"Book collection already contains {Book.objects.count()} books.")
    
    @staticmethod
    def get_all_books_sorted(category=None):
        """Get all books, optionally filtered by category."""
        if category and category.lower() != 'all':
            books = Book.objects.filter(category__iexact=category).order_by('title')
        else:
            books = Book.objects.order_by('title')
        return books
    
    @staticmethod
    def get_book_by_id(book_id):
        """Get a single book by its MongoDB ObjectId."""
        try:
            return Book.objects.get(id=book_id)
        except (Book.DoesNotExist, Exception):
            return None
    
    @staticmethod
    def createBook(genres, title, category, url, description, authors, pages, copies):
        """Create a new book."""
        book = Book(
            genres=genres,
            title=title,
            category=category,
            url=url,
            description=description,
            authors=authors,
            pages=pages,
            available=copies,
            copies=copies
        )
        book.save()
        return book
    
    def borrow_book(self):
        """
        Borrow a book by decreasing the available count.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Sanity check: Ensure there are available copies to borrow
        if self.available <= 0:
            return False, "No available copies to borrow. All copies are currently on loan."
        
        # Decrease available count
        self.available -= 1
        self.save()
        
        return True, f"Successfully borrowed '{self.title}'. {self.available} copies remaining."
    
    def return_book(self):
        """
        Return a book by increasing the available count.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Sanity check: Ensure the book was previously borrowed
        # (available count should be less than total copies)
        if self.available >= self.copies:
            return False, f"Cannot return '{self.title}'. All copies are already in the library."
        
        # Sanity check: Ensure available doesn't exceed copies
        if self.available < 0:
            # This shouldn't happen, but handle it gracefully
            self.available = 0
        
        # Increase available count
        self.available += 1
        self.save()
        
        return True, f"Successfully returned '{self.title}'. {self.available} of {self.copies} copies now available."
    
    def can_borrow(self):
        """
        Check if the book can be borrowed.
        
        Returns:
            bool: True if there are available copies, False otherwise
        """
        return self.available > 0
    
    def can_return(self):
        """
        Check if the book can be returned.
        
        Returns:
            bool: True if at least one copy is borrowed, False otherwise
        """
        return self.available < self.copies
    
    def get_borrowed_count(self):
        """
        Get the number of copies currently borrowed.
        
        Returns:
            int: Number of borrowed copies
        """
        return self.copies - self.available
    
    def get_author_string(self):
        """Get authors as a comma-separated string."""
        return ", ".join(self.authors)
    
    def get_genres_string(self):
        """Get genres as a comma-separated string."""
        return ", ".join(self.genres)
    
    def get_description_preview(self):
        """Get first and last paragraphs of description for preview."""
        if not self.description or len(self.description) == 0:
            return "No description available for this book."
        
        paragraphs = [p.strip() for p in self.description if p.strip()]
        
        if len(paragraphs) == 0:
            return "No description available for this book."
        elif len(paragraphs) == 1:
            return paragraphs[0]
        else:
            first = paragraphs[0]
            last = paragraphs[-1]
            return first + "<br><br>" + last
    
    def get_full_description(self):
        """Get full description with proper paragraph spacing."""
        if not self.description or len(self.description) == 0:
            return "No description available for this book."
        
        paragraphs = [p.strip() for p in self.description if p.strip()]
        return '<br><br>'.join(paragraphs)
    
    def to_dict(self):
        """Convert Book document to dictionary for template rendering."""
        return {
            'id': str(self.id),
            'title': self.title,
            'author': self.get_author_string(),
            'authors': self.authors,
            'category': self.category,
            'genres': self.get_genres_string(),
            'genres_list': self.genres,
            'pages': self.pages,
            'copies': self.copies,
            'available': self.available,
            'borrowed': self.get_borrowed_count(),
            'cover_image': self.url,
            'description': self.get_full_description(),
            'description_preview': self.get_description_preview(),
            'formatted_description': self.get_full_description(),
            'can_borrow': self.can_borrow(),
            'can_return': self.can_return()
        }
    
    def __str__(self):
        """String representation of Book."""
        return f"{self.title} by {self.get_author_string()}"