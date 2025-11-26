from database import db
from models import Reader, Librarian, Book, Loan, Reservation, Fine
from datetime import datetime, timedelta

class AuthDAO:
    @staticmethod
    def authenticate_reader(card_number, password):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM readers WHERE card_number = ?', (card_number,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            print(f"Читатель с картой {card_number} не найден")
            return None
            
        # Создаем объект читателя
        reader = Reader(*row)

        # Сравниваем пароли ПРОСТО как строки
        if reader.password == password:
            print(f"Пароль верный для {reader.name}")
            return reader
        else:
            print(f"Неверный пароль. Ожидалось: {reader.password}, получено: {password}")
            return None
    
    @staticmethod
    def authenticate_librarian(username, password):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM librarians WHERE username = ?', (username,)) 
        row = cursor.fetchone()
        conn.close()

        if not row:
            print(f"Библиотекарь с логином {username} не найден")
            return None
            
        # Создаем объект библиотекаря
        librarian = Librarian(*row)
        
        # Сравниваем пароли ПРОСТО как строки
        if librarian.password == password:
            print(f"Пароль верный для {librarian.name}")
            return librarian
        else:
            print(f"Неверный пароль. Ожидалось: {librarian.password}, получено: {password}")
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
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
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
    def get_all_readers():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM readers')
        readers = [Reader(*row) for row in cursor.fetchall()]
        conn.close()
        return readers

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

class LibrarianDAO:
    @staticmethod
    def get_all_librarians():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM librarians')
        librarians = [Librarian(*row) for row in cursor.fetchall()]
        conn.close()
        return librarians

class LoanDAO:
    @staticmethod
    def get_active_loans():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, b.title, r.name 
            FROM loans l 
            JOIN books b ON l.book_id = b.book_id 
            JOIN readers r ON l.reader_id = r.reader_id
            WHERE l.status = 'active'
        ''')
        loans = []
        for row in cursor.fetchall():
            loan = Loan(*row[:7])
            loan.book_title = row[7]
            loan.reader_name = row[8]
            loans.append(loan)
        conn.close()
        return loans
    
    # ДОБАВЛЕННЫЙ МЕТОД для создания выдачи
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

class ReservationDAO:
    @staticmethod
    def get_all_reservations():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, b.title, read.name
            FROM reservations r
            JOIN books b ON r.book_id = b.book_id
            JOIN readers read ON r.reader_id = read.reader_id
        ''')
        reservations = []
        for row in cursor.fetchall():
            reservation = Reservation(*row[:5])
            reservation.book_title = row[5]
            reservation.reader_name = row[6]
            reservations.append(reservation)
        conn.close()
        return reservations
    
    # ДОБАВЛЕННЫЙ МЕТОД для создания бронирования
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
    
    # ДОБАВЛЕННЫЙ МЕТОД для отмены бронирования
    @staticmethod
    def cancel_reservation(reservation_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reservations SET status = "cancelled" WHERE reservation_id = ?', 
                      (reservation_id,))
        conn.commit()
        conn.close()
        return True

class FineDAO:
    @staticmethod
    def get_all_fines():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, r.name 
            FROM fines f 
            JOIN readers r ON f.reader_id = r.reader_id
        ''')
        fines = []
        for row in cursor.fetchall():
            fine = Fine(*row[:5])
            fine.reader_name = row[5]
            fines.append(fine)
        conn.close()
        return fines