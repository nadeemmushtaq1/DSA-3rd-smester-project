"""
core/engine.py

Role: Central DSA Engine that manages all in-memory data structures:
- AVL Tree: for sorted book traversal (title/author)
- Hash Table: for O(1) ISBN lookups
- Trie: for prefix search on titles
- Author Trie: for prefix search on author names

Responsibilities:
- Load data from database into DSA structures
- Provide unified search interface for services
- Ensure fast, DSA-first lookups before touching DB
- Track performance metrics for all operations
"""

from typing import List, Optional
import time
from dsa.avl import AVLTree
from dsa.hash_table import HashTable
from dsa.trie import Trie
from models import Book
from sqlalchemy.orm import Session


class DSAEngine:
    """DSA Manager combining AVL, HashTable, Trie (for titles), and Author Trie"""
    def __init__(self, dataset_size: int = 1000, max_depth: int = 20):
        """
        Initialize DSA Engine with configurable parameters.
        :param dataset_size: Expected size of dataset for optimization
        :param max_depth: Maximum depth for tree structures
        """
        self.dataset_size = dataset_size
        self.max_depth = max_depth
        # Sorted tree for alphabetical listing
        self.avl = AVLTree()
        # Hash table for ISBN-based O(1) lookup
        self.hash_table = HashTable()
        # Trie for prefix-based search on titles
        self.trie = Trie()
        # Trie for prefix-based search on author names
        self.author_trie = Trie()
        
        # Performance metrics
        self.metrics = {
            "isbn_searches": 0,
            "title_searches": 0,
            "author_searches": 0,
            "total_search_time_ms": 0.0
        }

    # ---------------------------
    # Load from DB
    # ---------------------------
    def load_books(self, books: List[Book], db: Optional[Session] = None):
        """
        Populate all DSA structures with books
        :param books: list of Book objects from DB
        :param db: database session for logging
        """
        for book in books:
            # AVL insertion (for sorted traversal)
            self.avl.insert(book.title.lower(), book)

            # Hash table insertion (for O(1) ISBN lookup)
            self.hash_table.insert(book.isbn, book, db=db)

            # Trie insertion (for prefix search on titles)
            self.trie.insert(book.title, book, db=db)
            
            # Author Trie insertion (for prefix search on author names)
            if book.author and hasattr(book.author, 'author_name'):
                self.author_trie.insert(book.author.author_name, book, db=db)

    # ---------------------------
    # Search operations with performance metrics
    # ---------------------------
    def search_by_isbn(self, isbn: str) -> Optional[Book]:
        """Search book via Hash Table (O(1)) - Track performance"""
        start_time = time.time()
        book = self.hash_table.get(isbn)
        elapsed_ms = (time.time() - start_time) * 1000
        
        self.metrics["isbn_searches"] += 1
        self.metrics["total_search_time_ms"] += elapsed_ms
        
        return book

    def search_by_title_exact(self, title: str) -> Optional[Book]:
        """Exact match using AVL Tree - Track performance"""
        start_time = time.time()
        result = self.avl.search(title.lower())
        elapsed_ms = (time.time() - start_time) * 1000
        
        self.metrics["title_searches"] += 1
        self.metrics["total_search_time_ms"] += elapsed_ms
        
        return result

    def search_by_title_prefix(self, prefix: str) -> List[Book]:
        """Prefix search using Trie for title - Track performance"""
        start_time = time.time()
        books = self.trie.prefix_search(prefix)
        elapsed_ms = (time.time() - start_time) * 1000
        
        self.metrics["title_searches"] += 1
        self.metrics["total_search_time_ms"] += elapsed_ms
        
        return books

    def search_by_author_prefix(self, author_prefix: str) -> List[Book]:
        """Prefix search using Author Trie (O(m) where m = prefix length)"""
        start_time = time.time()
        books = self.author_trie.prefix_search(author_prefix)
        elapsed_ms = (time.time() - start_time) * 1000
        
        self.metrics["author_searches"] += 1
        self.metrics["total_search_time_ms"] += elapsed_ms
        
        return books

    def get_all_sorted(self) -> List[Book]:
        """Return all books sorted by title using AVL inorder traversal"""
        start_time = time.time()
        books = self.avl.inorder_traversal()
        elapsed_ms = (time.time() - start_time) * 1000
        
        self.metrics["total_search_time_ms"] += elapsed_ms
        
        return books
    
    def get_range(self, min_key: str, max_key: str) -> List[Book]:
        """
        Range query on AVL tree - return books with titles between min_key and max_key
        Useful for alphabetical range searches
        """
        start_time = time.time()
        result = []
        all_books = self.avl.inorder_traversal()
        
        # Filter books in range
        for book in all_books:
            if min_key.lower() <= book.title.lower() <= max_key.lower():
                result.append(book)
        
        elapsed_ms = (time.time() - start_time) * 1000
        self.metrics["total_search_time_ms"] += elapsed_ms
        
        return result

    # ---------------------------
    # Performance reporting
    # ---------------------------
    def get_performance_metrics(self) -> dict:
        """Return performance metrics for all searches"""
        return {
            "isbn_searches": self.metrics["isbn_searches"],
            "title_searches": self.metrics["title_searches"],
            "author_searches": self.metrics["author_searches"],
            "total_search_time_ms": round(self.metrics["total_search_time_ms"], 2),
            "avg_search_time_ms": round(
                self.metrics["total_search_time_ms"] / 
                max(1, sum([self.metrics["isbn_searches"], self.metrics["title_searches"], self.metrics["author_searches"]])),
                4
            )
        }

