import sqlite3
from datetime import datetime, timedelta
import hashlib

class Database:
    def __init__(self, db_name='library.db'):
        self.db_name = db_name
        self.create_tables()
        self.add_sample_data()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица книг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                year INTEGER,
                publisher TEXT,
                genre TEXT,
                description TEXT,
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1
            )
        ''')
        
        # Таблица библиотекарей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS librarians (
                librarian_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Таблица читателей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readers (
                reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                card_number TEXT UNIQUE NOT NULL,
                contact TEXT,
                password TEXT NOT NULL,
                status BOOLEAN DEFAULT 1
            )
        ''')
        
        # Таблица выдачи книг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                reader_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (reader_id) REFERENCES readers (reader_id)
            )
        ''')
        
        # Таблица бронирований
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                reader_id INTEGER NOT NULL,
                reservation_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (reader_id) REFERENCES readers (reader_id)
            )
        ''')
        
        # Таблица штрафов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fines (
                fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
                reader_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'unpaid',
                FOREIGN KEY (reader_id) REFERENCES readers (reader_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_sample_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM readers")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Добавляем библиотекарей
        cursor.executemany('''
            INSERT INTO librarians (name, username, password)
            VALUES (?, ?, ?)
        ''', [
            ('Анна Петрова', 'librarian1', self.hash_password('12345')),
            ('Иван Сидоров', 'librarian2', self.hash_password('54321'))
        ])
        
        # Добавляем читателей
        cursor.executemany('''
            INSERT INTO readers (name, card_number, contact, password, status)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('Иванов Иван', 'R001', 'ivanov@mail.ru', self.hash_password('pass1'), 1),
            ('Петрова Мария', 'R002', 'petrova@mail.ru', self.hash_password('pass2'), 1),
            ('Сидоров Алексей', 'R003', 'sidorov@mail.ru', self.hash_password('pass3'), 0)
        ])

        # Добавляем книги
        cursor.executemany('''
            INSERT INTO books (title, author, isbn, year, publisher, genre, description, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('Война и мир', 'Л.Н. Толстой', '978-5-389-00001-1', 1869, 'АСТ', 'Роман', 
             'Великий роман о войне 1812 года', 5, 3),
            ('Преступление и наказание', 'Ф.М. Достоевский', '978-5-389-00002-8', 1866, 'Эксмо', 'Роман',
             'Психологический роман о преступлении и его последствиях', 3, 2),
            ('Мастер и Маргарита', 'М.А. Булгаков', '978-5-389-00003-5', 1967, 'Азбука', 'Фантастика',
             'Мистический роман о дьяволе в Москве', 4, 4),
            ('Евгений Онегин', 'А.С. Пушкин', '978-5-389-00004-2', 1833, 'АСТ', 'Поэзия',
             'Роман в стихах о любви и судьбе', 2, 1),
            ('Отцы и дети', 'И.С. Тургенев', '978-5-389-00005-9', 1862, 'Эксмо', 'Роман',
             'Роман о конфликте поколений', 3, 3)
        ])

        # Добавляем выдачи книг
        cursor.executemany('''
            INSERT INTO loans (book_id, reader_id, issue_date, due_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            (1, 1, '2024-01-10', '2024-02-10', 'active'),
            (2, 2, '2024-01-12', '2024-02-12', 'active')
        ])
        
        # Добавляем бронирования
        cursor.executemany('''
            INSERT INTO reservations (book_id, reader_id, reservation_date, status)
            VALUES (?, ?, ?, ?)
        ''', [
            (3, 1, '2024-01-15', 'active'),
            (4, 2, '2024-01-16', 'active')
        ])

        # Добавляем штрафы
        cursor.executemany('''
            INSERT INTO fines (reader_id, amount, reason, status)
            VALUES (?, ?, ?, ?)
        ''', [
            (2, 150.50, 'Просрочка возврата книги', 'unpaid'),
            (3, 300.00, 'Потеря книги', 'paid')
        ])
        
        conn.commit()
        conn.close()
        print("✅ Тестовые данные добавлены в базу данных")

# Создаем глобальный объект базы данных
db = Database()

# Только если база пустая - добавляем тестовые данные
try:
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]
    conn.close()
    
    if book_count == 0:
        db.add_sample_data()
        print("Тестовые данные добавлены в базу данных")
    else:
        print("База данных уже содержит данные")
        
except:
    # Если таблиц нет - создаем и добавляем данные
    db.add_sample_data()