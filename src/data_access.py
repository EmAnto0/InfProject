from database import db
from models import Book, Copy, Reader

class BookDAO:
    @staticmethod
    def get_all_books():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books')
        books = [Book(*row) for row in cursor.fetchall()]
        conn.close()
        return books
    
    @staticmethod
    def add_book(book):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (title, author, isbn, year, publisher, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (book.title, book.author, book.isbn, book.year, book.publisher, book.category))
        conn.commit()
        conn.close()
    
    @staticmethod
    def search_books(query):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        books = [Book(*row) for row in cursor.fetchall()]
        conn.close()
        return books

class ReaderDAO:
    @staticmethod
    def get_all_readers():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM readers')
        readers = [Reader(*row) for row in cursor.fetchall()]
        conn.close()
        return readers
    
    @staticmethod
    def add_reader(reader):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO readers (name, card_number, contact, status)
            VALUES (?, ?, ?, ?)
        ''', (reader.name, reader.card_number, reader.contact, reader.status))
        conn.commit()
        conn.close()

class LoanDAO:
    @staticmethod
    def get_active_loans():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.loan_id, r.name, b.title, l.issue_date, l.due_date
            FROM loans l
            JOIN readers r ON l.reader_id = r.reader_id
            JOIN copies c ON l.copy_id = c.copy_id
            JOIN books b ON c.book_id = b.book_id
            WHERE l.status = 'active'
        ''')
        loans = cursor.fetchall()
        conn.close()
        return loans