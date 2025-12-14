# =============================================
# app.py
# FastAPI Entrypoint
# - Initializes database
# - Loads DSA engine (AVL + HashTable + Trie)
# - Ensures DB <-> DSA synchronization
# - Registers role-based routes
# - Acts as the thinnest possible server layer
# =============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from db import init_db, SessionLocal
from services.library import dsa_engine
from models import Book
from logger import log_system
from services.fine_scheduler import start_scheduler, stop_scheduler

from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.librarian import router as librarian_router
from routes.member import router as member_router


# -------------------------------------------------
# 1) Create FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="HIGH-LEVEL DSA LIBRARY SYSTEM",
    description="DSA-driven Library Management System (AVL, Hash, Trie)",
    version="1.0.0"
)


# -------------------------------------------------
# 2) CORS (allow frontend at localhost:3000 or 5173)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# -------------------------------------------------
# 3) Global DSA Engine from library service
# -------------------------------------------------
# dsa_engine is imported from services.library and used throughout

# -------------------------------------------------
# 4) App startup hook - Initialize DB and Load DSA
# -------------------------------------------------
@app.on_event("startup")
def startup_event():
    """
    At server startup:
    - Initialize DB
    - Load BOOK DATA from DB into DSA structures (Trie, AVL, Hash)
    - Start fine scheduler
    """
    print("[INFO] Initializing MySQL connection...")
    init_db()

    print("[INFO] Loading database books into DSA structures (Trie, AVL, Hash Table)...")
    db = SessionLocal()
    try:
        # Load all books from database
        books = db.query(Book).all()
        print(f"[INFO] Found {len(books)} books in database")
        
        # Populate DSA Engine with all books
        dsa_engine.load_books(books, db=db)
        
        log_system("STARTUP", f"Loaded {len(books)} books into DSA structures", 0)
        print(f"[INFO] ✓ DSA Engine initialized with {len(books)} books")
        print("[INFO]   - Trie (prefix search on titles)")
        print("[INFO]   - AVL Tree (sorted title traversal)")
        print("[INFO]   - Hash Table (O(1) ISBN lookup)")
    except Exception as e:
        print(f"[ERROR] Failed to load books into DSA: {str(e)}")
        raise
    finally:
        db.close()

    print("[INFO] Starting fine update scheduler...")
    start_scheduler()

    print("[INFO] ✓ System Ready - DSA Engine Active!")
    print("[INFO] Endpoints: /member/search/title, /member/search/author, /member/search/isbn")


# -------------------------------------------------
# 4b) App shutdown hook
# -------------------------------------------------
@app.on_event("shutdown")
def shutdown_event():
    """At server shutdown, stop the scheduler"""
    print("[INFO] Shutting down scheduler...")
    stop_scheduler()


# -------------------------------------------------
# 5) API ROUTES (Role-Based + Auth)
# -------------------------------------------------
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(librarian_router)
app.include_router(member_router)


# -------------------------------------------------
# 6) Root endpoint
# -------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "Online",
        "message": "High-Level DSA Library System",
        "DSA": "AVL + HASH + TRIE active"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


#python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload