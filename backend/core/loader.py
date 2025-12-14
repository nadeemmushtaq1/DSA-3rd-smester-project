"""
core/loader.py

DEPRECATED: This module is no longer used.
Use services.library.dsa_engine and app.py startup hook instead.

The DSA Engine is now initialized in app.py at startup, which properly:
1. Creates a singleton DSAEngine in services.library
2. Loads all books from database
3. Populates Trie, AVL, and Hash Table

This file is kept for backward compatibility only.
"""

from sqlalchemy.orm import Session
from models import Book
from core.engine import DSAEngine

# Singleton DSA Engine for the entire application
dsa_engine = DSAEngine()


def load_books_from_db(db: Session):
    """
    DEPRECATED: Use app.py startup hook instead.
    
    Load all books from the database into DSA structures
    :param db: SQLAlchemy session
    """
    # Fetch all books from DB
    books = db.query(Book).all()

    # Populate DSA engine (AVL, Hash, Trie)
    dsa_engine.load_books(books, db=db)

    print(f"[DSA ENGINE] Loaded {len(books)} books into AVL, HashTable, and Trie.")
    return dsa_engine
