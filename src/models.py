from datetime import datetime

class Book:
    def __init__(self, book_id=None, title="", author="", isbn="", year=None, publisher="", genre="", description="", total_copies=1, available_copies=1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.year = year
        self.publisher = publisher
        self.genre = genre
        self.description = description
        self.total_copies = total_copies
        self.available_copies = available_copies
    
    def __str__(self):
        return f"'{self.title}' - {self.author} ({self.year} | Доступно: {self.available_copies}/{self.total_copies})"

class Reader:
    def __init__(self, reader_id=None, name="", card_number="", contact="", password="", status=True):
        self.reader_id = reader_id
        self.name = name
        self.card_number = card_number
        self.contact = contact
        self.password = password
        self.status = status
    
    def __str__(self):
        status_str = "активен" if self.status else "заблокирован"
        return f"{self.name} (Карта: {self.card_number}) - {status_str})"
    
class Librarian:
    def __init__(self, librarian_id=None, name="", username="", password=""):
        self.librarian_id = librarian_id
        self.name = name
        self.username = username
        self.password = password
    
    def __str__(self):
        return f"{self.name} (Логин: {self.username})"
    
class Loan:
    def __init__(self, loan_id=None, book_id=None, reader_id=None, issue_date="", due_date="", return_date=None, status="active"):
        self.loan_id = loan_id
        self.book_id = book_id
        self.reader_id = reader_id
        self.issue_date = issue_date
        self.due_date = due_date
        self.return_date = return_date
        self.status = status
    
    def __str__(self):
        return f"Выдача #{self.loan_id} - до {self.due_date} ({self.status})"
    
class Reservation:
    def __init__(self, reservation_id=None, book_id=None, reader_id=None, reservation_date="", status="active"):
        self.reservation_id = reservation_id
        self.book_id = book_id
        self.reader_id = reader_id
        self.reservation_date = reservation_date
        self.status = status
    
    def __str__(self):
        return f"Бронирование #{self.reservation_id} от {self.reservation_date}"

class Fine:
    def __init__(self, fine_id=None, reader_id=None, amount=0.0, reason="", status="unpaid"):
        self.fine_id = fine_id
        self.reader_id = reader_id
        self.amount = amount
        self.reason = reason
        self.status = status
    
    def __str__(self):
        status_str = "оплачен" if self.status == 'paid' else "не оплачен"
        return f"Штраф: {self.amount} руб. - {self.reason} ({status_str})"