from app import db
from datetime import datetime
from app.models.users import User
from app.models.book import Book


class Loan(db.Document):
    """Loan model for tracking book loans."""
    
    meta = {
        'collection': 'loans',
        'ordering': ['-borrowDate']  # Descending order - most recent loans first
    }
    
    member = db.ReferenceField(User, required=True)
    book = db.ReferenceField(Book, required=True)
    borrowDate = db.DateTimeField(required=True)
    returnDate = db.DateTimeField(default=None)
    renewCount = db.IntField(default=0, min_value=0)
    
    @staticmethod
    def create_loan(user, book, borrow_date=None):
        """
        Create a new loan for a user.
        
        Args:
            user: User object making the loan
            book: Book object being borrowed
            borrow_date: Date of borrowing (defaults to now)
        
        Returns:
            tuple: (success: bool, message: str, loan: Loan or None)
        """
        # Sanity check 1: Check if user already has an unreturned loan for this book
        existing_loan = Loan.objects(
            member=user,
            book=book,
            returnDate=None  # Unreturned loan
        ).first()
        
        if existing_loan:
            return False, f"You already have an active loan for '{book.title}'. Please return it before borrowing again.", None
        
        # Sanity check 2: Check if book has available copies
        if not book.can_borrow():
            return False, f"No available copies of '{book.title}' to borrow.", None
        
        # Set borrow date to now if not provided
        if borrow_date is None:
            borrow_date = datetime.now()
        
        # Create the loan
        loan = Loan(
            member=user,
            book=book,
            borrowDate=borrow_date,
            returnDate=None,
            renewCount=0
        )
        
        # Update book's available count
        success, message = book.borrow_book()
        if not success:
            return False, message, None
        
        # Save the loan
        loan.save()
        
        return True, f"Successfully borrowed '{book.title}'.", loan
    
    @staticmethod
    def get_user_loans(user):
        """
        Retrieve all loans for a specific user.
        
        Args:
            user: User object
        
        Returns:
            QuerySet: All loans for the user, ordered by borrow date (newest first)
        """
        return Loan.objects(member=user).order_by('-borrowDate')
    
    @staticmethod
    def get_user_active_loans(user):
        """
        Retrieve all active (unreturned) loans for a specific user.
        
        Args:
            user: User object
        
        Returns:
            QuerySet: All active loans for the user
        """
        return Loan.objects(member=user, returnDate=None).order_by('-borrowDate')
    
    @staticmethod
    def get_user_returned_loans(user):
        """
        Retrieve all returned loans for a specific user.
        
        Args:
            user: User object
        
        Returns:
            QuerySet: All returned loans for the user
        """
        return Loan.objects(member=user, returnDate__ne=None).order_by('-returnDate')
    
    @staticmethod
    def get_loan_by_id(loan_id):
        """
        Retrieve a specific loan by its ID.
        
        Args:
            loan_id: MongoDB ObjectId of the loan
        
        Returns:
            Loan: Loan object or None if not found
        """
        try:
            return Loan.objects.get(id=loan_id)
        except (Loan.DoesNotExist, Exception):
            return None
    
    def renew_loan(self):
        """
        Renew a loan by updating the renew count and borrow date.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Sanity check 1: Loan must not be returned
        if self.returnDate is not None:
            return False, "Cannot renew a loan that has already been returned."
        
        # Sanity check 2: Check if there's a renewal limit (optional)
        MAX_RENEWALS = 3  # You can adjust this
        if self.renewCount >= MAX_RENEWALS:
            return False, f"Maximum renewal limit ({MAX_RENEWALS}) reached for '{self.book.title}'."
        
        # Update renew count and borrow date
        self.renewCount += 1
        self.borrowDate = datetime.now()
        self.save()
        
        return True, f"Successfully renewed '{self.book.title}'. Renewals: {self.renewCount}/{MAX_RENEWALS}"
    
    def return_loan(self, return_date=None):
        """
        Return a loan by setting the return date and updating book availability.
        
        Args:
            return_date: Date of return (defaults to now)
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Sanity check: Loan must not already be returned
        if self.returnDate is not None:
            return False, f"'{self.book.title}' has already been returned on {self.returnDate.strftime('%Y-%m-%d')}."
        
        # Set return date to now if not provided
        if return_date is None:
            return_date = datetime.now()
        
        # Update the loan
        self.returnDate = return_date
        self.save()
        
        # Update book's available count
        success, message = self.book.return_book()
        if not success:
            # Rollback the return date if book update fails
            self.returnDate = None
            self.save()
            return False, f"Failed to update book availability: {message}"
        
        return True, f"Successfully returned '{self.book.title}'."
    
    def delete_loan(self):
        """
        Delete a loan document.
        Only loans that have been returned can be deleted.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Sanity check: Only returned loans can be deleted
        if self.returnDate is None:
            return False, "Cannot delete an active loan. Please return the book first."
        
        book_title = self.book.title
        self.delete()
        
        return True, f"Successfully deleted loan record for '{book_title}'."
    
    def is_returned(self):
        """
        Check if the loan has been returned.
        
        Returns:
            bool: True if returned, False otherwise
        """
        return self.returnDate is not None
    
    def is_active(self):
        """
        Check if the loan is still active (not returned).
        
        Returns:
            bool: True if active, False otherwise
        """
        return self.returnDate is None
    
    def get_loan_duration_days(self):
        """
        Get the duration of the loan in days.
        
        Returns:
            int: Number of days from borrow date to return date (or now if not returned)
        """
        end_date = self.returnDate if self.returnDate else datetime.now()
        duration = end_date - self.borrowDate
        return duration.days
    
    def get_due_date(self):
        """
        Get the due date for the loan (2 weeks after borrow date).
        
        Returns:
            datetime: Due date
        """
        from datetime import timedelta
        return self.borrowDate + timedelta(days=14)
    
    def is_overdue(self, loan_period_days=14):
        """
        Check if the loan is overdue.
        
        Args:
            loan_period_days: Standard loan period in days (default: 14)
        
        Returns:
            bool: True if overdue, False otherwise
        """
        if self.returnDate is not None:
            return False  # Already returned
        
        due_date = self.get_due_date()
        return datetime.now() > due_date
    
    def get_days_overdue(self, loan_period_days=14):
        """
        Get the number of days the loan is overdue.
        
        Args:
            loan_period_days: Standard loan period in days (default: 14)
        
        Returns:
            int: Number of days overdue (0 if not overdue)
        """
        if not self.is_overdue(loan_period_days):
            return 0
        
        return self.get_loan_duration_days() - loan_period_days
    
    def to_dict(self):
        """
        Convert Loan document to dictionary for template rendering.
        
        Returns:
            dict: Loan data as dictionary
        """
        due_date = self.get_due_date()
        
        return {
            'id': str(self.id),
            'member_name': self.member.name,
            'member_email': self.member.email,
            'book_id': str(self.book.id),
            'book_title': self.book.title,
            'book_author': self.book.get_author_string(),
            'book_cover': self.book.url,
            'borrow_date': self.borrowDate.strftime('%Y-%m-%d %H:%M'),
            'borrow_date_short': self.borrowDate.strftime('%d %b %Y'),
            'due_date_short': due_date.strftime('%d %b %Y'),
            'return_date': self.returnDate.strftime('%Y-%m-%d %H:%M') if self.returnDate else None,
            'return_date_short': self.returnDate.strftime('%d %b %Y') if self.returnDate else None,
            'renew_count': self.renewCount,
            'is_returned': self.is_returned(),
            'is_active': self.is_active(),
            'loan_duration_days': self.get_loan_duration_days(),
            'is_overdue': self.is_overdue(),
            'days_overdue': self.get_days_overdue()
        }
    
    def __str__(self):
        """String representation of Loan."""
        status = "Returned" if self.returnDate else "Active"
        return f"{self.member.name} - {self.book.title} ({status})"