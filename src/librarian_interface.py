# librarian_interface.py
from data_access import BookDAO, ReaderDAO, LoanDAO, ReservationDAO, FineDAO
from models import Book
import os
from datetime import datetime, timedelta

class LibrarianInterface:
    def __init__(self, librarian):
        self.librarian = librarian
        self.run()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        print("=" * 50)
        print(f"БИБЛИОТЕЧНАЯ СИСТЕМА - БИБЛИОТЕКАРЬ")
        print(f"{self.librarian.name}")
        print("=" * 50)
    
    def show_menu(self):
        print("\nМЕНЮ БИБЛИОТЕКАРЯ:")
        print("1. Добавить новую книгу")
        print("2. Просмотреть все книги")
        print("3. Поиск книг")
        print("4. Управление читателями") 
        print("5. Просмотреть все выдачи")
        print("6. Управление бронированиями")
        print("7. Просмотреть штрафы")
        print("8. Статистика")
        print("9. Выйти")
    
    def add_new_book(self):
        self.clear_screen()
        self.display_header()
        print("\nДОБАВЛЕНИЕ НОВОЙ КНИГИ")
        
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
            print("Книга успешно добавлена!")
            
        except ValueError:
            print("Ошибка ввода данных!")
        except Exception as e:
            print(f"Ошибка при добавлении книги: {e}")
    
    def show_all_books(self):
        self.clear_screen()
        self.display_header()
        print("\nВСЕ КНИГИ В БИБЛИОТЕКЕ")
        
        books = BookDAO.get_all_books()
        if not books:
            print("В библиотеке пока нет книг!")
            return
        
        total_books = sum(book.total_copies for book in books)
        available_books = sum(book.available_copies for book in books)
        
        print(f"Всего книг: {total_books} | Доступно: {available_books}")
        print("-" * 60)
        
        for i, book in enumerate(books, 1):
            status = "+" if book.available_copies > 0 else "-"
            print(f"{i}. {status} {book}")
    
    def search_books(self):
        self.clear_screen()
        self.display_header()
        print("\n🔍 ПОИСК КНИГ")
        query = input("Введите название, автора или жанр: ").strip()
        
        if not query:
            print("Пустой запрос!")
            return
        
        books = BookDAO.search_books(query)
        if not books:
            print("Книги не найдены!")
            return
        
        print(f"\nНайдено книг: {len(books)}")
        for i, book in enumerate(books, 1):
            print(f"{i}. {book.title} - {book.author}")
            print(f"   Жанр: {book.genre} | Доступно: {book.available_copies}/{book.total_copies}")
            print()
    
    def manage_readers(self):
        self.clear_screen()
        self.display_header()
        print("\nУПРАВЛЕНИЕ ЧИТАТЕЛЯМИ")
        
        readers = ReaderDAO.get_all_readers()
        if not readers:
            print("Нет зарегистрированных читателей!")
            return
        
        print("\nСПИСОК ЧИТАТЕЛЕЙ:")
        for i, reader in enumerate(readers, 1):
            status = "Активен" if reader.status else "Заблокирован"
            print(f"{i}. {reader.name} | {reader.card_number} | {status}")
    
    def show_all_loans(self):
        self.clear_screen()
        self.display_header()
        print("\nВСЕ АКТИВНЫЕ ВЫДАЧИ")
        
        # Здесь можно добавить логику для просмотра всех выдач
        loans = LoanDAO.get_active_loans()
        if not loans:
            print("Нет активных выдач книг")
            return
        
        print(f"Всего активных выдач: {len(loans)}")
        print("-" * 70)
        
        for i, loan in enumerate(loans, 1):
            print(f"{i}. Читатель: {loan.reader_name}")
            print(f"   Книга: '{loan.book_title}'")
            print(f"   Выдана: {loan.issue_date}")
            print(f"   Вернуть до: {loan.due_date}")

            # Проверяем просрочку
            due_date = datetime.strptime(loan.due_date, '%Y-%m-%d')
            today = datetime.now()
            if today > due_date:
                days_overdue = (today - due_date).days
                print(f"   ПРОСРОЧЕНО на {days_overdue} дней")
            else:
                days_left = (due_date - today).days
                print(f"   Осталось дней: {days_left}")
            print()

    def manage_reservations(self):
        self.clear_screen()
        self.display_header()
        print("\nУПРАВЛЕНИЕ БРОНИРОВАНИЯМИ")
        
        reservations = ReservationDAO.get_all_reservations()
        if not reservations:
            print("Нет активных бронирований")
            return
        
        print(f"Всего активных бронирований: {len(reservations)}")
        print("-" * 60)
        
        for i, reservation in enumerate(reservations, 1):
            status = "Активно" if reservation.status == 'active' else "Отменено"
            print(f"{i}. Читатель: {reservation.reader_name}")
            print(f"   Книга: '{reservation.book_title}'")
            print(f"   Забронирована: {reservation.reservation_date}")
            print(f"   Статус: {status}")
            print()

    def show_all_fines(self):
        self.clear_screen()
        self.display_header()
        print("\nВСЕ ШТРАФЫ")
        
        fines = FineDAO.get_all_fines()
        if not fines:
            print("Нет штрафов в системе")
            return
        
        total_unpaid = sum(fine.amount for fine in fines if fine.status == 'unpaid')
        total_paid = sum(fine.amount for fine in fines if fine.status == 'paid')
        
        print(f"Всего штрафов: {len(fines)}")
        print(f"Общая сумма неоплаченных: {total_unpaid} руб.")
        print(f"Общая сумма оплаченных: {total_paid} руб.")
        print("-" * 60)
        
        for i, fine in enumerate(fines, 1):
            status = "Оплачен" if fine.status == 'paid' else "Не оплачен"
            print(f"{i}. Читатель: {fine.reader_name}")
            print(f"   Сумма: {fine.amount} руб.")
            print(f"   Причина: {fine.reason}")
            print(f"   Статус: {status}")
            print()

    def show_statistics(self):
        self.clear_screen()
        self.display_header()
        print("\nСТАТИСТИКА БИБЛИОТЕКИ")
        
        # Простая статистика
        books = BookDAO.get_all_books()
        readers = ReaderDAO.get_all_readers()
        loans = LoanDAO.get_active_loans()
        reservations = ReservationDAO.get_all_reservations()
        fines = FineDAO.get_all_fines()
        
        total_books = sum(book.total_copies for book in books)
        available_books = sum(book.available_copies for book in books)
        borrowed_books = total_books - available_books
        
        active_readers = sum(1 for reader in readers if reader.status)
        blocked_readers = sum(1 for reader in readers if not reader.status)
        
        unpaid_fines = sum(fine.amount for fine in fines if fine.status == 'unpaid')

        print("ОСНОВНАЯ СТАТИСТИКА:")
        print(f"   Книги в фонде: {total_books}")
        print(f"   Доступно для выдачи: {available_books}")
        print(f"   Выдано читателям: {borrowed_books}")
        print()
        
        print("ЧИТАТЕЛИ:")
        print(f"   Всего читателей: {len(readers)}")
        print(f"   Активных: {active_readers}")
        print(f"   Заблокированных: {blocked_readers}")
        print()
        
        print("АКТИВНОСТЬ:")
        print(f"   Активных выдач: {len(loans)}")
        active_reservations = len([r for r in reservations if r.status == 'active'])
        print(f"   Активных бронирований: {active_reservations}")
        print(f"   Неоплаченных штрафов: {unpaid_fines} руб.")

    def run(self):
        while True:
            self.clear_screen()
            self.display_header()
            self.show_menu()
            
            choice = input("\nВыберите действие (1-9): ").strip()
            
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
                self.show_all_fines()
            elif choice == '8':
                self.show_statistics()
            elif choice == '9':
                print("\nДо свидания!")
                break
            else:
                print("Неверный выбор!")
            
            input("\nНажмите Enter для продолжения...")