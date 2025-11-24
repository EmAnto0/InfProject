# check_database.py
from database import db

def check_all_data():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("=" * 50)
    print("ПРОВЕРКА ДАННЫХ В БАЗЕ")
    print("=" * 50)
    
    # Проверяем структуру таблицы readers
    print("\n📋 СТРУКТУРА ТАБЛИЦЫ READERS:")
    cursor.execute("PRAGMA table_info(readers)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Проверяем читателей
    print("\n📋 ЧИТАТЕЛИ:")
    cursor.execute('SELECT reader_id, name, card_number, contact, password, status FROM readers')
    readers = cursor.fetchall()
    for reader in readers:
        print(f"  ID: {reader[0]}, Имя: {reader[1]}")
        print(f"    Карта: {reader[2]}, Контакт: {reader[3]}")
        print(f"    Пароль: '{reader[4]}', Статус: {'Активен' if reader[5] else 'Заблокирован'}")
        print()
    
    # Проверяем библиотекарей
    print("\n👨‍💼 БИБЛИОТЕКАРИ:")
    cursor.execute('SELECT librarian_id, name, username, password FROM librarians')
    librarians = cursor.fetchall()
    for lib in librarians:
        print(f"  ID: {lib[0]}, Имя: {lib[1]}")
        print(f"    Логин: {lib[2]}, Пароль: '{lib[3]}'")
        print()
    
    # Проверяем книги
    print("\n📚 КНИГИ:")
    cursor.execute('SELECT book_id, title, author, available_copies FROM books')
    books = cursor.fetchall()
    for book in books:
        print(f"  ID: {book[0]}, '{book[1]}' - {book[2]}, Доступно: {book[3]}")
    
    conn.close()

if __name__ == "__main__":
    check_all_data()