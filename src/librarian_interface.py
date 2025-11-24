# librarian_interface.py
from data_access import AuthDAO, BookDAO, ReaderDAO, LoanDAO, ReservationDAO
from models import Book
import os

class LibrarianInterface:
    def __init__(self, librarian):
        self.librarian = librarian
        self.run()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        print("=" * 50)
        print(f"📚 БИБЛИОТЕЧНАЯ СИСТЕМА - БИБЛИОТЕКАРЬ")
        print(f"👤 {self.librarian.name}")
        print("=" * 50)
    
    def show_menu(self):
        print("\n📋 МЕНЮ БИБЛИОТЕКАРЯ:")
        print("1. 📖 Добавить новую книгу")
        print("2. 📚 Просмотреть все книги")
        print("3. 🔍 Поиск книг")
        print("4. 👥 Управление читателями") 
        print("5. 📋 Просмотреть все выдачи")
        print("6. 📊 Статистика")
        print("7. 🚪 Выйти")
    
    def add_new_book(self):
        self.clear_screen()
        self.display_header()
        print("\n📖 ДОБАВЛЕНИЕ НОВОЙ КНИГИ")
        
        try:
            title = input("Название книги: ").strip()
            author = input("Автор: ").strip()
            isbn = input("ISBN (опционально): ").strip() or None
            year = input("Год издания: ").strip()
            publisher = input("Издательство: ").strip()
            genre = input("Жанр: ").strip()
            description = input("Описание: ").strip()
            total_copies = int(input("Количество экземпляров: ").strip())
            
            book = Book(
                title=title,
                author=author,
                isbn=isbn,
                year=int(year) if year else None,
                publisher=publisher,
                genre=genre,
                description=description,
                total_copies=total_copies,
                available_copies=total_copies
            )
            
            BookDAO.add_book(book)
            print("✅ Книга успешно добавлена!")
            
        except ValueError:
            print("❌ Ошибка ввода данных!")
        except Exception as e:
            print(f"❌ Ошибка при добавлении книги: {e}")
    
    def show_all_books(self):
        self.clear_screen()
        self.display_header()
        print("\n📚 ВСЕ КНИГИ В БИБЛИОТЕКЕ")
        
        books = BookDAO.get_all_books()
        if not books:
            print("❌ В библиотеке пока нет книг!")
            return
        
        total_books = sum(book.total_copies for book in books)
        available_books = sum(book.available_copies for book in books)
        
        print(f"Всего книг: {total_books} | Доступно: {available_books}")
        print("-" * 60)
        
        for i, book in enumerate(books, 1):
            status = "✅" if book.available_copies > 0 else "❌"
            print(f"{i}. {status} {book}")
    
    def search_books(self):
        self.clear_screen()
        self.display_header()
        print("\n🔍 ПОИСК КНИГ")
        query = input("Введите название, автора или жанр: ").strip()
        
        if not query:
            print("❌ Пустой запрос!")
            return
        
        books = BookDAO.search_books(query)
        if not books:
            print("❌ Книги не найдены!")
            return
        
        print(f"\n📚 Найдено книг: {len(books)}")
        for i, book in enumerate(books, 1):
            print(f"{i}. {book}")
    
    def manage_readers(self):
        self.clear_screen()
        self.display_header()
        print("\n👥 УПРАВЛЕНИЕ ЧИТАТЕЛЯМИ")
        
        readers = ReaderDAO.get_all_readers()
        if not readers:
            print("❌ Нет зарегистрированных читателей!")
            return
        
        print("\n📋 СПИСОК ЧИТАТЕЛЕЙ:")
        for i, reader in enumerate(readers, 1):
            status = "✅ Активен" if reader.status else "❌ Заблокирован"
            print(f"{i}. {reader.name} | {reader.card_number} | {status}")
    
    def show_all_loans(self):
        self.clear_screen()
        self.display_header()
        print("\n📋 ВСЕ АКТИВНЫЕ ВЫДАЧИ")
        
        # Здесь можно добавить логику для просмотра всех выдач
        print("📊 Функция просмотра всех выдач будет реализована в следующей версии")
    
    def show_statistics(self):
        self.clear_screen()
        self.display_header()
        print("\n📊 СТАТИСТИКА БИБЛИОТЕКИ")
        
        # Простая статистика
        books = BookDAO.get_all_books()
        readers = ReaderDAO.get_all_readers()
        
        total_books = sum(book.total_copies for book in books)
        available_books = sum(book.available_copies for book in books)
        borrowed_books = total_books - available_books
        
        print(f"📚 Всего книг: {total_books}")
        print(f"✅ Доступно: {available_books}")
        print(f"📖 Выдано: {borrowed_books}")
        print(f"👥 Зарегистрировано читателей: {len(readers)}")
        print(f"👨‍💼 Библиотекарей: 2")  # Хардкод, можно улучшить
    
    def run(self):
        while True:
            self.clear_screen()
            self.display_header()
            self.show_menu()
            
            choice = input("\nВыберите действие (1-7): ").strip()
            
            if choice == '1':
                self.add_new_book()
            elif choice == '2':
                self.show_all_books()
            elif choice == '3':
                self.search_books()
            elif choice == '4':
                self.manage_readers()
            elif choice == '5':
                self.show_all_loans()
            elif choice == '6':
                self.show_statistics()
            elif choice == '7':
                print("\n👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")
            
            input("\nНажмите Enter для продолжения...")