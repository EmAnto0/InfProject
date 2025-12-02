import os

def reset_database():
    # Удаляем старый файл базы данных
    if os.path.exists('library.db'):
        os.remove('library.db')
        print("Старая база данных удалена")
    
    # Пересоздаем базу
    from database import db
    print("Новая база данных создана")

if __name__ == "__main__":
    reset_database()
