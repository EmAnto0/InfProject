# lab5_export.py
import json
import csv
import xml.etree.ElementTree as ET
import yaml
import os
import sys
from datetime import datetime

# Добавляем путь к модулям для надежности
sys.path.append(os.path.dirname(__file__))

from data_access import BookDAO, ReaderDAO, LoanDAO, ReservationDAO, FineDAO

def create_output_folder():
    """Создает папку out в корне проекта"""
    # Поднимаемся на уровень выше из папки src
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Поднимаемся из src в корень
    out_dir = os.path.join(project_root, 'out')
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print(f"Папка 'out' создана: {out_dir}")
    else:
        # Очищаем папку от старых файлов
        for file in os.listdir(out_dir):
            file_path = os.path.join(out_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Не удалось удалить {file_path}: {e}")
        print(f"Папка 'out' очищена: {out_dir}")
    
    return out_dir

def get_all_library_data():
    """Собирает все данные из библиотеки"""
    print("Сбор данных из базы...")
    
    try:
        books = BookDAO.get_all_books()
        readers = ReaderDAO.get_all_readers()
        loans = LoanDAO.get_active_loans()
        reservations = ReservationDAO.get_all_reservations()
        fines = FineDAO.get_all_fines()
        
        # Подготавливаем данные для экспорта
        data = {
            'library_info': {
                'name': 'Библиотечная система',
                'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_records': len(books) + len(readers) + len(loans) + len(reservations) + len(fines)
            },
            'books': [book.__dict__ for book in books],
            'readers': [reader.__dict__ for reader in readers],
            'loans': [loan.__dict__ for loan in loans],
            'reservations': [reservation.__dict__ for reservation in reservations],
            'fines': [fine.__dict__ for fine in fines]
        }
        
        print(f"Собрано данных:")
        print(f"  Книги: {len(books)}")
        print(f"  Читатели: {len(readers)}")
        print(f"  Активные выдачи: {len(loans)}")
        print(f"  Бронирования: {len(reservations)}")
        print(f"  Штрафы: {len(fines)}")
        
        return data
        
    except Exception as e:
        print(f"Ошибка при сборе данных: {e}")
        return {}

def save_to_json(data, filename):
    """Сохраняет данные в формате JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"JSON создан: {filename}")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении JSON: {e}")
        return False

def save_to_csv(data, filename):
    """Сохраняет данные в формате CSV"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Тип', 'ID', 'Название/Имя', 'Автор/Контакты', 'Год', 'Доступно', 'Статус'])
            
            # Книги
            for book in data.get('books', []):
                writer.writerow([
                    'Книга', 
                    book.get('book_id', ''), 
                    book.get('title', ''), 
                    book.get('author', ''), 
                    book.get('year', ''), 
                    book.get('available_copies', ''),
                    'Доступна' if book.get('available_copies', 0) > 0 else 'Нет в наличии'
                ])
            
            # Читатели
            for reader in data.get('readers', []):
                status = 'Активен' if reader.get('status') else 'Заблокирован'
                writer.writerow([
                    'Читатель',
                    reader.get('reader_id', ''),
                    reader.get('name', ''),
                    reader.get('contact', ''),
                    '',
                    '',
                    status
                ])
                
        print(f"CSV создан: {filename}")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении CSV: {e}")
        return False

def save_to_xml(data, filename):
    """Сохраняет данные в формате XML"""
    try:
        root = ET.Element('library')
        
        # Добавляем информацию о библиотеке
        info_elem = ET.SubElement(root, 'info')
        ET.SubElement(info_elem, 'name').text = data.get('library_info', {}).get('name', 'Библиотека')
        ET.SubElement(info_elem, 'export_date').text = data.get('library_info', {}).get('export_date', '')
        ET.SubElement(info_elem, 'total_records').text = str(data.get('library_info', {}).get('total_records', 0))
        
        # Книги
        books_elem = ET.SubElement(root, 'books')
        for book in data.get('books', []):
            book_elem = ET.SubElement(books_elem, 'book')
            for key, value in book.items():
                if value is not None:
                    elem = ET.SubElement(book_elem, key)
                    elem.text = str(value)
        
        # Читатели
        readers_elem = ET.SubElement(root, 'readers')
        for reader in data.get('readers', []):
            reader_elem = ET.SubElement(readers_elem, 'reader')
            for key, value in reader.items():
                if value is not None:
                    elem = ET.SubElement(reader_elem, key)
                    elem.text = str(value)
        
        tree = ET.ElementTree(root)
        
        # Сохраняем с правильным форматированием
        with open(filename, 'wb') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
            tree.write(f, encoding='utf-8', xml_declaration=False)
            
        print(f"XML создан: {filename}")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении XML: {e}")
        return False

def save_to_yaml(data, filename):
    """Сохраняет данные в формате YAML"""
    try:
        # Очищаем данные от None значений для YAML
        def clean_for_yaml(obj):
            if isinstance(obj, dict):
                return {k: clean_for_yaml(v) for k, v in obj.items() if v is not None}
            elif isinstance(obj, list):
                return [clean_for_yaml(item) for item in obj]
            else:
                return obj
        
        cleaned_data = clean_for_yaml(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(cleaned_data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"YAML создан: {filename}")
        return True
        
    except Exception as e:
        print(f"Ошибка при сохранении YAML: {e}")
        return False

def main():
    """Основная функция экспорта"""
    print("=" * 50)
    print("ЛАБОРАТОРНАЯ РАБОТА №5 - ЭКСПОРТ ДАННЫХ")
    print("=" * 50)
    
    # Проверяем доступность базы данных
    if not os.path.exists('library.db'):
        print("База данных 'library.db' не найдена!")
        print("Запустите main.py сначала чтобы создать базу данных")
        return
    
    # Создаем папку для результатов в корне проекта
    out_dir = create_output_folder()
    
    # Получаем данные
    library_data = get_all_library_data()
    
    if not library_data:
        print("Нет данных для экспорта!")
        return
    
    # Экспортируем в разные форматы
    print("\nНачинаем экспорт данных...")
    
    # Создаем файлы во всех форматах
    results = {
        'JSON': save_to_json(library_data, os.path.join(out_dir, 'data.json')),
        'CSV': save_to_csv(library_data, os.path.join(out_dir, 'data.csv')),
        'XML': save_to_xml(library_data, os.path.join(out_dir, 'data.xml')),
        'YAML': save_to_yaml(library_data, os.path.join(out_dir, 'data.yaml'))
    }
    
    # Итоги
    print("\n" + "=" * 50)
    print("ЭКСПОРТ ЗАВЕРШЕН!")
    print("=" * 50)
    
    successful = sum(results.values())
    total = len(results)
    
    print(f"Результаты: {successful}/{total} форматов создано успешно")
    
    print("\nСозданные файлы:")
    print("-" * 40)
    
    files = os.listdir(out_dir)
    for file in sorted(files):
        file_path = os.path.join(out_dir, file)
        file_size = os.path.getsize(file_path)
        print(f"  {file} ({file_size} байт)")
    
    print(f"\nВсе файлы сохранены в: {out_dir}")
    print("=" * 50)

if __name__ == "__main__":
    main()