"""
Database Reset Script
This script resets the library database to the initial state with data from books.py
"""

from app import app, db
from app.models.book import Book
from app.models.users import User
from app.models.loan import Loan
from books import all_books


def reset_database():
    """Reset the database to initial state."""
    
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    
    with app.app_context():
        # Step 1: Delete all existing loans
        print("\n[1/4] Deleting all loans...")
        loan_count = Loan.objects.count()
        Loan.objects.delete()
        print(f"      Deleted {loan_count} loan(s).")
        
        # Step 2: Delete all existing books
        print("\n[2/4] Deleting all books...")
        book_count = Book.objects.count()
        Book.objects.delete()
        print(f"      Deleted {book_count} book(s).")
        
        # Step 3: Delete all existing users
        print("\n[3/4] Deleting all users...")
        user_count = User.objects.count()
        User.objects.delete()
        print(f"      Deleted {user_count} user(s).")
        
        # Step 4: Re-initialize with default data
        print("\n[4/4] Initializing default data...")
        
        # Re-create default users
        print("\n      Creating default users...")
        admin = User(
            email='admin@lib.sg',
            name='Admin',
            is_admin=True
        )
        admin.set_password('12345')
        admin.save()
        print(f"      ✓ Created admin user: {admin.email}")
        
        user = User(
            email='poh@lib.sg',
            name='Peter Oh',
            is_admin=False
        )
        user.set_password('12345')
        user.save()
        print(f"      ✓ Created regular user: {user.email}")
        
        # Re-initialize books from books.py
        print("\n      Creating books from books.py...")
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
            print(f"      ✓ Created book: {book.title}")
        
        # Summary
        print("\n" + "=" * 60)
        print("DATABASE RESET COMPLETE!")
        print("=" * 60)
        print(f"\nFinal counts:")
        print(f"  - Users: {User.objects.count()}")
        print(f"  - Books: {Book.objects.count()}")
        print(f"  - Loans: {Loan.objects.count()}")
        print("\nDefault login credentials:")
        print("  Admin:")
        print("    Email: admin@lib.sg")
        print("    Password: 12345")
        print("  Regular User:")
        print("    Email: poh@lib.sg")
        print("    Password: 12345")
        print("=" * 60)


if __name__ == '__main__':
    # Prompt for confirmation
    print("\n⚠️  WARNING: This will delete ALL data in the database!")
    print("This includes all users, books, and loans.")
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        reset_database()
    else:
        print("\nDatabase reset cancelled.")
        print("No changes were made to the database.")