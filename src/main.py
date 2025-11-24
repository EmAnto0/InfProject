# main.py
from data_access import AuthDAO, BookDAO, ReaderDAO
from reader_interface import ReaderInterface
from librarian_interface import LibrarianInterface
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear_screen()
        print("=" * 50)
        print("СИСТЕМА УЧЕТА КНИГ В БИБЛИОТЕКЕ")
        print("=" * 50)
        print("\n1. Вход для читателя")
        print("2. Вход для библиотекаря") 
        print("3. Выход")
        
        choice = input("\nВыберите тип входа (1-3): ").strip()
        
        if choice == '1':
            reader_login()
        elif choice == '2':
            librarian_login()
        elif choice == '3':
            print("\nДо свидания!")
            break
        else:
            print("❌ Неверный выбор!")
            input("Нажмите Enter для продолжения...")

def reader_login():
    clear_screen()
    print("👤 ВХОД ДЛЯ ЧИТАТЕЛЯ")
    print("-" * 30)
    
    card_number = input("Номер читательского билета: ").strip()
    password = input("Пароль: ").strip()
    
    reader = AuthDAO.authenticate_reader(card_number, password)
    if reader:
        if reader.status:
            print(f"\n✅ Добро пожаловать, {reader.name}!")
            input("Нажмите Enter для продолжения...")
            ReaderInterface(reader)
        else:
            print("❌ Ваш аккаунт заблокирован! Обратитесь к библиотекарю.")
            input("Нажмите Enter для продолжения...")
    else:
        print("❌ Неверный номер читательского билета или пароль!")
        input("Нажмите Enter для продолжения...")

def librarian_login():
    clear_screen()
    print("👨‍💼 ВХОД ДЛЯ БИБЛИОТЕКАРЯ")
    print("-" * 30)
    
    username = input("Логин: ").strip()
    password = input("Пароль: ").strip()
    
    librarian = AuthDAO.authenticate_librarian(username, password)
    if librarian:
        print(f"\n✅ Добро пожаловать, {librarian.name}!")
        input("Нажмите Enter для продолжения...")
        LibrarianInterface(librarian)
    else:
        print("❌ Неверный логин или пароль!")
        input("Нажмите Enter для продолжения...")

if __name__ == "__main__":
    main()