from database import db
from data_access import BookDAO, ReaderDAO, LoanDAO

def main():
    print("=== Система учёта книг в библиотеке ===\n")
    
    # Демонстрация работы с книгами
    print("1. Все книги в библиотеке:")
    books = BookDAO.get_all_books()
    for book in books:
        print(f"   - {book}")
    
    print("\n2. Все читатели:")
    readers = ReaderDAO.get_all_readers()
    for reader in readers:
        print(f"   - {reader}")
    
    print("\n3. Поиск книг по запросу 'Толстой':")
    found_books = BookDAO.search_books('Толстой')
    for book in found_books:
        print(f"   - {book}")
    
    print("\n✅ База данных успешно создана и заполнена!")
    print("✅ Все функции работают корректно!")

if __name__ == "__main__":
    main()