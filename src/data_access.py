from database import db
from models import Reader, Librarian, Book, Loan, Reservation, Fine
import hashlib

class AuthDAO:
    @staticmethod
    def authenticate_reader(card_number, password):
        conn = db.get_connection()
        cursor = conn.cursor()
        hashed_password = db.hash_password(password)
        cursor.execute('SELECT * FROM readers WHERE card_number = ? AND password = ?', 
                      (card_number, hashed_password))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Reader(*row)
        return None
    
    @staticmethod
    def authenticate_librarian(username, password):
        conn = db.get_connection()
        cursor = conn.cursor()
        hashed_password = db.hash_password(password)
        cursor.execute('SELECT * FROM librarians WHERE username = ? AND password = ?', 
                      (username, hashed_password))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Librarian(*row)
        return None

class BookDAO:
    @staticmethod
    def get_all_books():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books ORDER BY title')
        books = [Book(*row) for row in cursor.fetchall()]
        conn.close()
        return books
    
    @staticmethod
    def search_books(query):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR genre LIKE ? OR isbn LIKE ?
            ORDER BY title
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        books = [Book(*row) for row in cursor.fetchall()]
        conn.close()
        return books
    
    @staticmethod
    def get_book_by_id(book_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Book(*row)
        return None
    
    @staticmethod
    def add_book(book):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (title, author, isbn, year, publisher, genre, description, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (book.title, book.author, book.isbn, book.year, book.publisher, book.genre, book.description, book.total_copies, book.available_copies))
        conn.commit()
        conn.close()

    @staticmethod
    def update_book_copies(book_id, change):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE books SET available_copies = available_copies + ? WHERE book_id = ?', 
                      (change, book_id))
        conn.commit()
        conn.close()

class ReaderDAO:
    @staticmethod
    def get_reader_by_id(reader_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM readers WHERE reader_id = ?', (reader_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Reader(*row)
        return None

class LoanDAO:
    @staticmethod
    def get_reader_loans(reader_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, b.title 
            FROM loans l 
            JOIN books b ON l.book_id = b.book_id 
            WHERE l.reader_id = ? AND l.status = 'active'
        ''', (reader_id,))
        loans = []
        for row in cursor.fetchall():
            loan = Loan(*row[:7])
            loan.book_title = row[7]
            loans.append(loan)
        conn.close()
        return loans
    
    @staticmethod
    def get_reader_reservations(reader_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, b.title 
            FROM reservations r 
            JOIN books b ON r.book_id = b.book_id 
            WHERE r.reader_id = ? AND r.status = 'active'
        ''', (reader_id,))
        reservations = []
        for row in cursor.fetchall():
            reservation = Reservation(*row[:5])
            reservation.book_title = row[5]
            reservations.append(reservation)
        conn.close()
        return reservations
    
    @staticmethod
    def get_reader_fines(reader_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM fines WHERE reader_id = ?', (reader_id,))
        fines = [Fine(*row) for row in cursor.fetchall()]
        conn.close()
        return fines
    
class LoanDAO:
    @staticmethod
    def create_loan(book_id, reader_id, days=30):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        from datetime import datetime, timedelta
        issue_date = datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO loans (book_id, reader_id, issue_date, due_date)
            VALUES (?, ?, ?, ?)
        ''', (book_id, reader_id, issue_date, due_date))
        
        # Уменьшаем количество доступных книг
        BookDAO.update_book_copies(book_id, -1)
        
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def return_loan(loan_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Получаем информацию о выдаче
        cursor.execute('SELECT book_id FROM loans WHERE loan_id = ?', (loan_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        
        book_id = result[0]
        
        # Обновляем выдачу
        return_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            UPDATE loans SET return_date = ?, status = 'returned' 
            WHERE loan_id = ?
        ''', (return_date, loan_id))
        
        # Увеличиваем количество доступных книг
        BookDAO.update_book_copies(book_id, 1)
        
        conn.commit()
        conn.close()
        return True
    
class ReservationDAO:
    @staticmethod
    def create_reservation(book_id, reader_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        reservation_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            INSERT INTO reservations (book_id, reader_id, reservation_date)
            VALUES (?, ?, ?)
        ''', (book_id, reader_id, reservation_date))
        
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def cancel_reservation(reservation_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reservations SET status = "cancelled" WHERE reservation_id = ?', 
                      (reservation_id,))
        conn.commit()
        conn.close()
        return True
