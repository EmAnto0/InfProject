# reader_interface.py
from data_access import BookDAO, ReaderDAO, ReservationDAO
import os

class ReaderInterface:
    def __init__(self, reader):
        self.reader = reader
        self.run()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        print("=" * 50)
        print(f"БИБЛИОТЕЧНАЯ СИСТЕМА - ЧИТАТЕЛЬ")
        print(f"{self.reader.name} (Карта: {self.reader.card_number})")
        print("=" * 50)
    
    def show_menu(self):
        print("\nМЕНЮ ЧИТАТЕЛЯ:")
        print("1. Поиск книг")
        print("2. Просмотреть все книги") 
        print("3. Мои текущие выдачи")
        print("4. Мои бронирования")
        print("5. Мои штрафы")
        print("6. Выйти")
    
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
        
        print(f"\nНайдено книг: {len(books)}")
        for i, book in enumerate(books, 1):
            status = "Доступна" if book.available_copies > 0 else "Нет в наличии"
            print(f"{i}. {book.title} - {book.author} | {status}")
    
    def show_all_books(self):
        self.clear_screen()
        self.display_header()
        print("\nВСЕ КНИГИ В БИБЛИОТЕКЕ")
        
        books = BookDAO.get_all_books()
        if not books:
            print("❌ В библиотеке пока нет книг!")
            return
        
        for i, book in enumerate(books, 1):
            status = "✅ Доступна" if book.available_copies > 0 else "❌ Нет в наличии"
            print(f"{i}. {book} | {status}")
    
    def show_my_loans(self):
        self.clear_screen()
        self.display_header()
        print("\n📖 МОИ ТЕКУЩИЕ ВЫДАЧИ")
        
        loans = ReaderDAO.get_reader_loans(self.reader.reader_id)
        if not loans:
            print("✅ У вас нет текущих выдач")
            return
        
        for i, loan in enumerate(loans, 1):
            print(f"{i}. Книга: '{loan.book_title}'")
            print(f"   📅 Выдана: {loan.issue_date}")
            print(f"   ⏰ Вернуть до: {loan.due_date}")
            print()
    
    def show_my_reservations(self):
        self.clear_screen()
        self.display_header()
        print("\n📅 МОИ БРОНИРОВАНИЯ")
        
        reservations = ReaderDAO.get_reader_reservations(self.reader.reader_id)
        if not reservations:
            print("✅ У вас нет активных бронирований")
            return
        
        for i, reservation in enumerate(reservations, 1):
            print(f"{i}. Книга: '{reservation.book_title}'")
            print(f"   📅 Забронирована: {reservation.reservation_date}")
            print()
        
        # Опция отмены бронирования
        if reservations:
            choice = input("\nОтменить бронирование? (введите номер или 0 для отмены): ")
            if choice.isdigit() and 1 <= int(choice) <= len(reservations):
                reservation_id = reservations[int(choice)-1].reservation_id
                if ReservationDAO.cancel_reservation(reservation_id):
                    print("✅ Бронирование отменено!")
    
    def show_my_fines(self):
        self.clear_screen()
        self.display_header()
        print("\n💰 МОИ ШТРАФЫ")
        
        fines = ReaderDAO.get_reader_fines(self.reader.reader_id)
        if not fines:
            print("✅ У вас нет штрафов")
            return
        
        total_unpaid = sum(fine.amount for fine in fines if fine.status == 'unpaid')
        
        for i, fine in enumerate(fines, 1):
            print(f"{i}. {fine}")
        
        print(f"\n💵 Общая сумма неоплаченных штрафов: {total_unpaid} руб.")
    
    def run(self):
        while True:
            self.clear_screen()
            self.display_header()
            self.show_menu()
            
            choice = input("\nВыберите действие (1-6): ").strip()
            
            if choice == '1':
                self.search_books()
            elif choice == '2':
                self.show_all_books()
            elif choice == '3':
                self.show_my_loans()
            elif choice == '4':
                self.show_my_reservations()
            elif choice == '5':
                self.show_my_fines()
            elif choice == '6':
                print("\n👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")
            
            input("\nНажмите Enter для продолжения...")