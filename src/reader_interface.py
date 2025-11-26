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
        # Проверяем актуальные задолженности
        has_unpaid_fines = ReaderDAO.has_unpaid_fines(self.reader.reader_id)
        status_text = "Активен" if not has_unpaid_fines else "Заблокирован (неоплаченные штрафы)"
        print("=" * 50)
        print("БИБЛИОТЕЧНАЯ СИСТЕМА - ЧИТАТЕЛЬ")
        print(f"Пользователь: {self.reader.name} (Карта: {self.reader.card_number})")
        print(f"Статус: {status_text}")
        print("=" * 50)

    
    def show_menu(self):
        print("\nМЕНЮ ЧИТАТЕЛЯ:")
        print("1. Поиск книг")
        print("2. Просмотреть все книги") 
        print("3. Забронировать книгу")
        print("4. Мои текущие выдачи")
        print("5. Мои бронирования")
        print("6. Мои штрафы")
        print("0. Выйти")

    def search_books(self, show_reserve_option=False):
        self.clear_screen()
        self.display_header()
        print("\nПОИСК КНИГ")
        query = input("Введите название, автора или жанр: ").strip()
        
        if not query:
            print("Пустой запрос!")
            return []
        
        books = BookDAO.search_books(query)
        if not books:
            print("Книги не найдены!")
            return []
        
        print(f"\nНайдено книг: {len(books)}")
        for i, book in enumerate(books, 1):
            status = "Доступна" if book.available_copies > 0 else "Нет в наличии"
            print(f"{i}. {book.title} - {book.author} | {status}")

            if book.available_copies > 0:
                print(f"   ID книги: {book.book_id} | Жанр: {book.genre} | Год: {book.year}")
            print()
        
        if show_reserve_option and books:
            choice = input("Хотите забронировать книгу? (введите номер книги или 0 для отмены): ").strip()
            if choice != '0' and choice != '':
                try:
                    book_index = int(choice) - 1
                    if 0 <= book_index < len(books):
                        selected_book = books[book_index]
                        if selected_book.available_copies > 0:
                            self.reserve_selected_book(selected_book)
                        else:
                            print("Эта книга недоступна для бронирования!")
                    else:
                        print("Неверный номер книги!")
                except ValueError:
                    print("Пожалуйста, введите число!")
        
        return books
    
    def show_all_books(self):
        self.clear_screen()
        self.display_header()
        print("\nВСЕ КНИГИ В БИБЛИОТЕКЕ")
        
        books = BookDAO.get_all_books()
        if not books:
            print("В библиотеке пока нет книг!")
            return
        
        for i, book in enumerate(books, 1):
            status = "Доступна" if book.available_copies > 0 else "Нет в наличии"
            print(f"{i}. {book.title} - {book.author} | {status}")
    
    def reserve_book(self):
        self.clear_screen()
        self.display_header()
        print("\nБРОНИРОВАНИЕ КНИГИ")
        
        # Проверяем есть ли неоплаченные штрафы (актуальная блокировка)
        has_unpaid_fines = ReaderDAO.has_unpaid_fines(self.reader.reader_id)
        
        if has_unpaid_fines:
            print("\nВНИМАНИЕ: У вас есть неоплаченные штрафы!")
            print("Бронирование книг недоступно до полной оплаты задолженностей.")
            
            choice = input("\nХотите просмотреть информацию о задолженностях? (да/нет): ").strip().lower()
            if choice in ['да', 'д', 'y', 'yes', '1']:
                self.show_my_fines()
            else:
                print("Обратитесь к библиотекарю для решения вопроса.")
            
            input("\nНажмите Enter для возврата в меню...")
            return
        
        print("Сначала найдем книгу для бронирования...")

        # Используем поиск с опцией бронирования
        books = self.search_books(show_reserve_option=True)
        
        # Если книги найдены, но пользователь не выбрал книгу в поиске,
        # предлагаем выбрать из найденных результатов
        if books and not any(book.available_copies > 0 for book in books):
            print("\nК сожалению, среди найденных книг нет доступных для бронирования.")
        elif books:
            # Есть доступные книги, но пользователь не выбрал в поиске
            available_books = [book for book in books if book.available_copies > 0]
            if available_books:
                print("\nДоступные для бронирования книги из результатов поиска:")
                for i, book in enumerate(available_books, 1):
                    print(f"{i}. {book.title} - {book.author}")
                
                try:
                    choice = input("\nВыберите номер книги для бронирования (0 для отмены): ").strip()
                    if choice == '0':
                        return
                    
                    book_index = int(choice) - 1
                    if 0 <= book_index < len(available_books):
                        selected_book = available_books[book_index]
                        self.reserve_selected_book(selected_book)
                    else:
                        print("Неверный номер книги!")
                except ValueError:
                    print("Пожалуйста, введите число!")

    def reserve_selected_book(self, book):
        """Бронирует выбранную книгу"""
        print(f"\nВы выбрали: {book.title} - {book.author}")
        confirm = input("Подтвердить бронирование? (да/нет): ").strip().lower()
        
        if confirm in ['да', 'д', 'y', 'yes', '1']:
            success, message = ReaderDAO.reserve_book(book.book_id, self.reader.reader_id)
            
            if success:
                print(f"Успех: {message}")
                print(f"Книга '{book.title}' успешно забронирована!")
            else:
                print(f"Ошибка: {message}")
        else:
            print("Бронирование отменено.")
    
    def show_my_loans(self):
        self.clear_screen()
        self.display_header()
        print("\nМОИ ТЕКУЩИЕ ВЫДАЧИ")
        
        loans = ReaderDAO.get_reader_loans(self.reader.reader_id)
        if not loans:
            print("У вас нет текущих выдач")
            return
        
        for i, loan in enumerate(loans, 1):
            print(f"{i}. Книга: '{loan.book_title}'")
            print(f"   Выдана: {loan.issue_date}")
            print(f"   Вернуть до: {loan.due_date}")
            print()
    
    def show_my_reservations(self):
        self.clear_screen()
        self.display_header()
        print("\nМОИ БРОНИРОВАНИЯ")
        
        reservations = ReaderDAO.get_reader_reservations(self.reader.reader_id)
        if not reservations:
            print("У вас нет активных бронирований")
            return
        
        for i, reservation in enumerate(reservations, 1):
            print(f"{i}. Книга: '{reservation.book_title}'")
            print(f"   Забронирована: {reservation.reservation_date}")
            print()
        
        # Опция отмены бронирования
        if reservations:
            choice = input("\nОтменить бронирование? (введите номер или 0 для отмены): ")
            if choice.isdigit() and 1 <= int(choice) <= len(reservations):
                confirm = input("Подтвердить отмену бронирования? (да/нет): ").strip().lower()
                if confirm in ['1', 'да', 'д', 'y', 'yes']:
                    reservation_id = reservations[int(choice)-1].reservation_id
                    if ReservationDAO.cancel_reservation(reservation_id):
                        print("Бронирование отменено!")
    
    def show_my_fines(self):
        self.clear_screen()
        self.display_header()
        print("\nМОИ ШТРАФЫ")
        
        fines = ReaderDAO.get_reader_fines(self.reader.reader_id)
        if not fines:
            print("У вас нет штрафов")
            return
        
        unpaid_fines = [f for f in fines if f.status == 'unpaid']
        total_unpaid = sum(fine.amount for fine in unpaid_fines)
        
        print(f"\nОбщая сумма неоплаченных штрафов: {total_unpaid} руб.")
        print(f"Количество неоплаченных штрафов: {len(unpaid_fines)}")
    
        if unpaid_fines:
            print("\nНЕОПЛАЧЕННЫЕ ШТРАФЫ:")
            for i, fine in enumerate(unpaid_fines, 1):
                print(f"{i}. Сумма: {fine.amount} руб.")
                print(f"   Причина: {fine.reason}")
                print()
        
        paid_fines = [f for f in fines if f.status == 'paid']
        if paid_fines:
            print("\nОПЛАЧЕННЫЕ ШТРАФЫ (история):")
            for i, fine in enumerate(paid_fines, 1):
                print(f"{i}. Сумма: {fine.amount} руб.")
                print(f"   Причина: {fine.reason}")
                print()
            
            if total_unpaid > 0:
                print("Для разблокировки аккаунта необходимо оплатить все штрафы.")
                print("Обратитесь к библиотекарю.")

    def run(self):
        while True:
            self.clear_screen()
            self.display_header()
            self.show_menu()
            
            choice = input("\nВыберите действие или нажмите Enter для выхода: ").strip()
            
            if choice == '1':
                self.search_books()
            elif choice == '2':
                self.show_all_books()
            elif choice == '3':
                self.reserve_book()
            elif choice == '4':
                self.show_my_loans()
            elif choice == '5':
                self.show_my_reservations()
            elif choice == '6':
                self.show_my_fines()
            elif choice == '0' or choice == '':
                print("\nДо свидания!")
                break
            else:
                print("Неверный выбор!")
            
            input("\nНажмите Enter для продолжения...")