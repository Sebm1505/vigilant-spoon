from mongoengine import Document, StringField, ListField, IntField, BooleanField
from books import all_books
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, Document):
    """
    User document class for MongoDB storage.
    Maps to the User collection in the database.
    """
    email = StringField(required=True, unique=True, max_length=100)
    password_hash = StringField(required=True)
    name = StringField(required=True, max_length=100)
    is_admin = BooleanField(default=False)
    
    # MongoDB collection name
    meta = {
        'collection': 'users',
        'indexes': ['email']
    }
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_by_email(cls, email):
        """
        Get a user by email address.
        
        Args:
            email (str): User's email address
        
        Returns:
            User or None: User document if found, None otherwise
        """
        try:
            return cls.objects.get(email=email.lower())
        except cls.DoesNotExist:
            return None
    
    def __str__(self):
        """String representation of User."""
        return f"{self.name} ({self.email})"

class Book(Document):
    """
    Book document class for MongoDB storage.
    Maps to the Book collection in the database.
    """
    # Define fields matching the class diagram
    genres = ListField(StringField(), required=True)
    title = StringField(required=True, max_length=200)
    category = StringField(required=True, max_length=50)
    url = StringField(required=True)  # Cover image URL
    description = ListField(StringField(), required=True)
    authors = ListField(StringField(), required=True)
    pages = IntField(required=True)
    available = IntField(required=True, min_value=0)
    copies = IntField(required=True, min_value=0)
    
    # MongoDB collection name
    meta = {
        'collection': 'books',
        'ordering': ['title']  # Default ordering by title
    }
    
    @classmethod
    def initialize_collection(cls):
        """
        Initialize the Book collection from all_books data.
        Only populates if the collection is empty.
        """
        # Check if collection is empty
        if cls.objects.count() == 0:
            print("Book collection is empty. Initializing from all_books data...")
            
            # Create Book documents from all_books
            for book_data in all_books:
                book = cls(
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
            
            print(f"Successfully initialized {cls.objects.count()} books in the database.")
        else:
            print(f"Book collection already contains {cls.objects.count()} books.")
    
    @classmethod
    def get_all_books_sorted(cls, category=None):
        """
        Get all books, optionally filtered by category, sorted alphabetically by title.
        
        Args:
            category (str, optional): Filter by category. If None or 'all', returns all books.
        
        Returns:
            QuerySet: Filtered and sorted books
        """
        if category and category.lower() != 'all':
            # Filter by category (case-insensitive)
            books = cls.objects.filter(category__iexact=category).order_by('title')
        else:
            # Return all books, sorted by title
            books = cls.objects.order_by('title')
        
        return books
    
    @classmethod
    def get_book_by_id(cls, book_id):
        """
        Get a single book by its MongoDB ObjectId.
        
        Args:
            book_id (str): MongoDB ObjectId as string
        
        Returns:
            Book or None: Book document if found, None otherwise
        """
        try:
            return cls.objects.get(id=book_id)
        except (cls.DoesNotExist, Exception):
            return None
    
    def get_author_string(self):
        """
        Get authors as a comma-separated string.
        
        Returns:
            str: Authors joined by comma and space
        """
        return ", ".join(self.authors)
    
    def get_genres_string(self):
        """
        Get genres as a comma-separated string.
        
        Returns:
            str: Genres joined by comma and space
        """
        return ", ".join(self.genres)
    
    def get_description_preview(self):
        """
        Get first and last paragraphs of description for preview.
        
        Returns:
            str: HTML-formatted preview with first and last paragraphs
        """
        if not self.description or len(self.description) == 0:
            return "No description available for this book."
        
        paragraphs = [p.strip() for p in self.description if p.strip()]
        
        if len(paragraphs) == 0:
            return "No description available for this book."
        elif len(paragraphs) == 1:
            return paragraphs[0]
        else:
            # Return first and last paragraphs with spacing
            first = paragraphs[0]
            last = paragraphs[-1]
            return first + "<br><br>" + last
    
    def get_full_description(self):
        """
        Get full description with proper paragraph spacing.
        
        Returns:
            str: HTML-formatted full description
        """
        if not self.description or len(self.description) == 0:
            return "No description available for this book."
        
        paragraphs = [p.strip() for p in self.description if p.strip()]
        return '<br><br>'.join(paragraphs)
    
    def to_dict(self):
        """
        Convert Book document to dictionary for template rendering.
        
        Returns:
            dict: Book data as dictionary
        """
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
            'cover_image': self.url,
            'description': self.get_full_description(),
            'description_preview': self.get_description_preview(),
            'formatted_description': self.get_full_description()
        }
    
    def __str__(self):
        """String representation of Book."""
        return f"{self.title} by {self.get_author_string()}"