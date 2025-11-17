import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name='library.db'):
        self.db_name = db_name
        self.create_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
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
                category TEXT
            )
        ''')
        
        # Таблица экземпляров книг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copies (
                copy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                barcode TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'available',
                condition TEXT DEFAULT 'good',
                FOREIGN KEY (book_id) REFERENCES books (book_id)
            )
        ''')
        
        # Таблица читателей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readers (
                reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                card_number TEXT UNIQUE NOT NULL,
                contact TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Таблица выдачи книг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                copy_id INTEGER NOT NULL,
                reader_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (copy_id) REFERENCES copies (copy_id),
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
        
        # Добавляем тестовые книги
        cursor.executemany('''
            INSERT INTO books (title, author, isbn, year, publisher, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            ('Война и мир', 'Л.Н. Толстой', '978-5-389-00001-1', 1869, 'АСТ', 'Роман'),
            ('Преступление и наказание', 'Ф.М. Достоевский', '978-5-389-00002-8', 1866, 'Эксмо', 'Роман'),
            ('Мастер и Маргарита', 'М.А. Булгаков', '978-5-389-00003-5', 1967, 'Азбука', 'Фантастика')
        ])
        
        # Добавляем экземпляры книг
        cursor.executemany('''
            INSERT INTO copies (book_id, barcode, status, condition)
            VALUES (?, ?, ?, ?)
        ''', [
            (1, 'COPY001', 'available', 'good'),
            (1, 'COPY002', 'available', 'good'),
            (2, 'COPY003', 'available', 'excellent'),
            (3, 'COPY004', 'available', 'good')
        ])
        
        # Добавляем читателей
        cursor.executemany('''
            INSERT INTO readers (name, card_number, contact, status)
            VALUES (?, ?, ?, ?)
        ''', [
            ('Иванов Иван', 'READER001', 'ivanov@mail.ru', 'active'),
            ('Петрова Мария', 'READER002', 'petrova@mail.ru', 'active')
        ])
        
        conn.commit()
        conn.close()

# Создаем базу данных при импорте
db = Database()
db.add_sample_data()