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
        print(f"Пользователь: {self.librarian.name}")
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
        print("0. Выйти")
    
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
            unpaid_fines = FineDAO.get_reader_unpaid_fines_count(reader.reader_id)
            print(f"{i}. {reader.name} | {reader.card_number} | {status} | Неоплаченных штрафов: {unpaid_fines}")

        print("\nОпции:")
        print("1. Изменить статус читателя")
        print("2. Добавить штраф")
        print("0. Назад")
        
        choice = input("\nВыберите опцию: ").strip()
        
        if choice == '1':
            self.change_reader_status(readers)
        elif choice == '2':
            self.add_fine_to_reader(readers)
        elif choice == '0':
            return
        else:
            print("Неверный выбор!")

    def change_reader_status(self, readers):
        """Изменяет статус читателя с автоматической синхронизацией штрафов"""
        try:
            choice = input("\nВыберите номер читателя для изменения статуса: ").strip()
            if not choice.isdigit():
                print("Неверный ввод!")
                return
            
            reader_index = int(choice) - 1
            if 0 <= reader_index < len(readers):
                selected_reader = readers[reader_index]
                current_status = "Активен" if selected_reader.status else "Заблокирован"
                new_status = not selected_reader.status  # Инвертируем статус
                new_status_text = "Активен" if new_status else "Заблокирован"
                
                print(f"\nЧитатель: {selected_reader.name}")
                print(f"Текущий статус: {current_status}")
                print(f"Новый статус: {new_status_text}")
                
                # Проверяем неоплаченные штрафы при разблокировке
                if new_status:  # Если разблокируем
                    unpaid_fines = FineDAO.get_reader_unpaid_fines_count(selected_reader.reader_id)
                    if unpaid_fines > 0:
                        print(f"\nВНИМАНИЕ: У читателя {unpaid_fines} неоплаченных штрафов!")
                        confirm = input("Все штрафы будут помечены как оплаченные. Продолжить? (да/нет): ").strip().lower()
                        if confirm not in ['1', 'да', 'д', 'y', 'yes']:
                            print("Операция отменена.")
                            return
                
                confirm = input(f"\nПодтвердить изменение статуса? (да/нет): ").strip().lower()
                if confirm in ['1', 'да', 'д', 'y', 'yes']:
                    success, message = ReaderDAO.update_reader_status(selected_reader.reader_id, new_status)
                    if success:
                        print(f"Успех: {message}")
                    else:
                        print(f"Ошибка: {message}")
                else:
                    print("Операция отменена.")
            else:
                print("Неверный номер читателя!")
                
        except ValueError:
            print("Пожалуйста, введите число!")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    def add_fine_to_reader(self, readers):
        """Добавляет штраф читателю с автоматической блокировкой"""
        try:
            choice = input("\nВыберите номер читателя для добавления штрафа: ").strip()
            if not choice.isdigit():
                print("Неверный ввод!")
                return
            
            reader_index = int(choice) - 1
            if 0 <= reader_index < len(readers):
                selected_reader = readers[reader_index]
                
                print(f"\nЧитатель: {selected_reader.name}")
                amount = input("Сумма штрафа: ").strip()
                reason = input("Причина штрафа: ").strip()
                
                if not amount.replace('.', '').isdigit() or float(amount) <= 0:
                    print("Неверная сумма штрафа!")
                    return
                
                if not reason:
                    print("Причина штрафа не может быть пустой!")
                    return
                
                print(f"\nСумма: {amount} руб.")
                print(f"Причина: {reason}")
                print("Читатель будет автоматически заблокирован при добавлении штрафа.")
                
                confirm = input("\nПодтвердить добавление штрафа? (да/нет): ").strip().lower()
                if confirm in ['1', 'да', 'д', 'y', 'yes']:
                    success, message = FineDAO.add_fine_with_status_update(
                        selected_reader.reader_id, float(amount), reason
                    )
                    if success:
                        print(f"Успех: {message}")
                    else:
                        print(f"Ошибка: {message}")
                else:
                    print("Операция отменена.")
            else:
                print("Неверный номер читателя!")
                
        except ValueError:
            print("Пожалуйста, введите корректные данные!")
        except Exception as e:
            print(f"Ошибка: {e}")

    def manage_fines(self):
        """Управление штрафами"""
        self.clear_screen()
        self.display_header()
        print("\nУПРАВЛЕНИЕ ШТРАФАМИ")
        
        fines = FineDAO.get_all_fines()
        if not fines:
            print("Нет штрафов в системе")
            return
        
        print(f"\nВсего штрафов: {len(fines)}")
        print("-" * 60)
        
        for i, fine in enumerate(fines, 1):
            status = "ОПЛАЧЕН" if fine.status == 'paid' else "НЕ ОПЛАЧЕН"
            print(f"{i}. Читатель: {fine.reader_name}")
            print(f"   Сумма: {fine.amount} руб.")
            print(f"   Причина: {fine.reason}")
            print(f"   Статус: {status}")
            print(f"   ID штрафа: {fine.fine_id}")
            print()
        
        print("Опции:")
        print("1. Изменить статус штрафа")
        print("0. Назад")
        
        choice = input("\nВыберите опцию: ").strip()
        
        if choice == '1':
            self.change_fine_status(fines)
        elif choice == '0':
            return
        else:
            print("Неверный выбор!")
    
    def change_fine_status(self, fines):
        """Изменяет статус штрафа"""
        try:
            choice = input("\nВыберите номер штрафа для изменения статуса: ").strip()
            if not choice.isdigit():
                print("Неверный ввод!")
                return
            
            fine_index = int(choice) - 1
            if 0 <= fine_index < len(fines):
                selected_fine = fines[fine_index]
                current_status = "Оплачен" if selected_fine.status == 'paid' else "Не оплачен"
                
                print(f"\nШтраф: {selected_fine.amount} руб.")
                print(f"Читатель: {selected_fine.reader_name}")
                print(f"Причина: {selected_fine.reason}")
                print(f"Текущий статус: {current_status}")
                
                new_status = "paid" if selected_fine.status == 'unpaid' else "unpaid"
                new_status_text = "Оплачен" if new_status == 'paid' else "Не оплачен"
                
                print(f"Новый статус: {new_status_text}")
                
                confirm = input("\nПодтвердить изменение статуса? (да/нет): ").strip().lower()
                if confirm in ['да', 'д', 'y', 'yes', '1']:
                    success, message = FineDAO.update_fine_status(selected_fine.fine_id, new_status)
                    if success:
                        print(f"Успех: {message}")
                    else:
                        print(f"Ошибка: {message}")
                else:
                    print("Операция отменена.")
            else:
                print("Неверный номер штрафа!")
                
        except ValueError:
            print("Пожалуйста, введите число!")
        except Exception as e:
            print(f"Ошибка: {e}")

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
            
            choice = input("\nВыберите действие или нажмите Enter для выхода: ").strip()
            
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
            elif choice == '0' or choice == '':
                print("\nДо свидания!")
                break
            else:
                print("Неверный выбор!")
            
            input("\nНажмите Enter для продолжения...")