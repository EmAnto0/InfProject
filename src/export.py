# lab5_export.py
import json
import csv
import xml.etree.ElementTree as ET
import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(__file__))

from data_access import BookDAO, ReaderDAO, LoanDAO, ReservationDAO, FineDAO

# Проверяем доступность YAML с подробной диагностикой
try:
    import yaml
    YAML_AVAILABLE = True
    YAML_VERSION = getattr(yaml, '__version__', 'unknown')
    print(f"✅ PyYAML доступен (версия: {YAML_VERSION})")
except ImportError as e:
    print(f"❌ PyYAML не установлен: {e}")
    print("💡 Установите: python -m pip install PyYAML==6.0.1")
    YAML_AVAILABLE = False
except Exception as e:
    print(f"⚠️  Неожиданная ошибка при импорте YAML: {e}")
    YAML_AVAILABLE = False

def create_output_folder():
    """Создает папку out, если её нет"""
    if not os.path.exists('out'):
        os.makedirs('out')
        print("✅ Папка 'out' создана")
    else:
        # Очищаем папку от старых файлов
        for file in os.listdir('out'):
            file_path = os.path.join('out', file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"⚠️  Не удалось удалить {file_path}: {e}")
        print("✅ Папка 'out' очищена")

def get_all_library_data():
    """Собирает все данные из библиотеки"""
    print("📥 Сбор данных из базы...")
    
    try:
        books = BookDAO.get_all_books()
        readers = ReaderDAO.get_all_readers()
        loans = LoanDAO.get_active_loans()
        reservations = ReservationDAO.get_all_reservations()
        fines = FineDAO.get_all_fines()
        
        # Функция для очистки данных
        def clean_data(obj):
            if hasattr(obj, '__dict__'):
                # Если это объект, берем его __dict__
                data = obj.__dict__.copy()
            else:
                data = obj.copy() if isinstance(obj, dict) else obj
                
            # Удаляем приватные атрибуты (начинающиеся с _)
            if isinstance(data, dict):
                data = {k: v for k, v in data.items() if not k.startswith('_')}
                # Рекурсивно очищаем вложенные данные
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        data[key] = clean_data(value)
            elif isinstance(data, list):
                data = [clean_data(item) for item in data]
                
            return data
        
        data = {
            'library_info': {
                'name': 'Библиотечная система',
                'export_date': str(os.path.getctime('library.db')),
                'total_records': len(books) + len(readers) + len(loans) + len(reservations) + len(fines)
            },
            'books': [clean_data(book) for book in books],
            'readers': [clean_data(reader) for reader in readers],
            'loans': [clean_data(loan) for loan in loans],
            'reservations': [clean_data(reservation) for reservation in reservations],
            'fines': [clean_data(fine) for fine in fines]
        }
        
        print(f"✅ Собрано данных:")
        print(f"   📚 Книги: {len(books)}")
        print(f"   👥 Читатели: {len(readers)}")
        print(f"   📖 Активные выдачи: {len(loans)}")
        print(f"   📅 Бронирования: {len(reservations)}")
        print(f"   💰 Штрафы: {len(fines)}")
        
        return data
        
    except Exception as e:
        print(f"❌ Ошибка при сборе данных: {e}")
        import traceback
        traceback.print_exc()
        return {}

def save_to_json(data, filename):
    """Сохраняет данные в формате JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ JSON создан: {filename}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении JSON: {e}")
        return False

def save_to_csv(data, filename):
    """Сохраняет данные в формате CSV"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # Основная таблица
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
                
        print(f"✅ CSV создан: {filename}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении CSV: {e}")
        return False

def save_to_xml(data, filename):
    """Сохраняет данные в формате XML"""
    try:
        root = ET.Element('library')
        
        # Добавляем информацию о библиотеке
        info_elem = ET.SubElement(root, 'info')
        ET.SubElement(info_elem, 'name').text = data.get('library_info', {}).get('name', 'Библиотека')
        ET.SubElement(info_elem, 'export_date').text = data.get('library_info', {}).get('export_date', '')
        
        # Книги
        books_elem = ET.SubElement(root, 'books')
        for book in data.get('books', []):
            book_elem = ET.SubElement(books_elem, 'book')
            for key, value in book.items():
                if value is not None and key != 'library_info':
                    elem = ET.SubElement(book_elem, key.replace(' ', '_'))
                    elem.text = str(value)
        
        # Читатели
        readers_elem = ET.SubElement(root, 'readers')
        for reader in data.get('readers', []):
            reader_elem = ET.SubElement(readers_elem, 'reader')
            for key, value in reader.items():
                if value is not None:
                    elem = ET.SubElement(reader_elem, key.replace(' ', '_'))
                    elem.text = str(value)
        
        tree = ET.ElementTree(root)
        
        # Сохраняем с правильным форматированием
        with open(filename, 'wb') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
            tree.write(f, encoding='utf-8', xml_declaration=False)
            
        print(f"✅ XML создан: {filename}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении XML: {e}")
        return False

def save_to_yaml(data, filename):
    """Сохраняет данные в формате YAML"""
    if not YAML_AVAILABLE:
        print("❌ YAML недоступен. Пропускаем создание YAML файла.")
        return False
        
    try:
        # Дополнительная очистка данных для YAML
        def yaml_safe_data(obj):
            if isinstance(obj, dict):
                return {k: yaml_safe_data(v) for k, v in obj.items() 
                       if v is not None and not k.startswith('_')}
            elif isinstance(obj, list):
                return [yaml_safe_data(item) for item in obj]
            elif isinstance(obj, (int, float, str, bool)):
                return obj
            else:
                return str(obj)
        
        safe_data = yaml_safe_data(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(safe_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"✅ YAML создан: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении YAML: {e}")
        print("💡 Попробуйте: python -m pip install --upgrade PyYAML")
        return False

def main():
    """Основная функция экспорта"""
    print("=" * 60)
    print("📊 ЛАБОРАТОРНАЯ РАБОТА №5 - ЭКСПОРТ ДАННЫХ")
    print("=" * 60)
    
    # Проверяем доступность базы данных
    if not os.path.exists('library.db'):
        print("❌ База данных 'library.db' не найдена!")
        print("💡 Запустите main.py сначала чтобы создать базу данных")
        return
    
    # Создаем папку
    create_output_folder()
    
    # Получаем данные
    library_data = get_all_library_data()
    
    if not library_data:
        print("❌ Нет данных для экспорта!")
        return
    
    # Экспортируем в разные форматы
    print("\n💾 Начинаем экспорт данных...")
    
    results = {
        'JSON': save_to_json(library_data, 'out/data.json'),
        'CSV': save_to_csv(library_data, 'out/data.csv'),
        'XML': save_to_xml(library_data, 'out/data.xml'),
        'YAML': save_to_yaml(library_data, 'out/data.yaml')
    }
    
    # Итоги
    print("\n" + "=" * 60)
    print("🎉 ЭКСПОРТ ЗАВЕРШЕН!")
    print("=" * 60)
    
    successful = sum(results.values())
    total = len(results)
    
    print(f"📈 Результаты: {successful}/{total} форматов создано успешно")
    
    print("\n📁 Созданные файлы в папке 'out/':")
    print("-" * 40)
    
    files = os.listdir('out')
    for file in sorted(files):
        file_path = os.path.join('out', file)
        file_size = os.path.getsize(file_path)
        status = "✅" if file_size > 0 else "❌"
        print(f"   {status} {file} ({file_size} байт)")
    
    if not results['YAML']:
        print("\n⚠️  YAML файл не создан")
        print("   Проверьте установку PyYAML: python -m pip install PyYAML==6.0.1")
    
    print("=" * 60)

if __name__ == "__main__":
    main()