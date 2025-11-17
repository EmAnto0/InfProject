from datetime import datetime

class Book:
    def __init__(self, book_id=None, title="", author="", isbn="", year=None, publisher="", category=""):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year
        self.publisher = publisher
        self.category = category
    
    def __str__(self):
        return f"{self.title} - {self.author} ({self.year})"

class Copy:
    def __init__(self, copy_id=None, book_id=None, barcode="", status="available", condition="good"):
        self.copy_id = copy_id
        self.book_id = book_id
        self.barcode = barcode
        self.status = status
        self.condition = condition

class Reader:
    def __init__(self, reader_id=None, name="", card_number="", contact="", status="active"):
        self.reader_id = reader_id
        self.name = name
        self.card_number = card_number
        self.contact = contact
        self.status = status
    
    def __str__(self):
        return f"{self.name} ({self.card_number})"