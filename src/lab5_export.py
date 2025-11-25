# lab5_export.py
import json
import csv
import xml.etree.ElementTree as ET
import yaml
import os
from data_access import BookDAO, ReaderDAO, LoanDAO, ReservationDAO, FineDAO

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
        
def export_library_data():
    print("📊 Экспорт данных библиотеки...")
    
    # Получаем данные
    books = BookDAO.get_all_books()
    readers = ReaderDAO.get_all_readers()
    
    # Подготавливаем данные для экспорта
    data = {
        'books': [book.__dict__ for book in books],
        'readers': [reader.__dict__ for reader in readers]
    }
    
    # JSON
    with open('out/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # CSV
    with open('out/data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Тип', 'ID', 'Название/Имя', 'Автор/Контакты', 'Доступно'])
        for book in books:
            writer.writerow(['Книга', book.book_id, book.title, book.author, book.available_copies])
        for reader in readers:
            writer.writerow(['Читатель', reader.reader_id, reader.name, reader.contact, reader.status])
    
    # XML
    root = ET.Element('library')
    for book in books:
        book_elem = ET.SubElement(root, 'book')
        ET.SubElement(book_elem, 'id').text = str(book.book_id)
        ET.SubElement(book_elem, 'title').text = book.title
        ET.SubElement(book_elem, 'author').text = book.author
        ET.SubElement(book_elem, 'available').text = str(book.available_copies)
    
    tree = ET.ElementTree(root)
    with open('out/data.xml', 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
    
    # YAML
    with open('out/data.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    print("✅ Данные экспортированы в папку 'out/'")

if __name__ == "__main__":
    create_output_folder()
    export_library_data()