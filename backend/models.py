from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw):  self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)


class Category(db.Model):
    __tablename__ = 'categories'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    books       = db.relationship('Book', backref='category', lazy=True)


class Book(db.Model):
    __tablename__ = 'books'
    id                 = db.Column(db.Integer, primary_key=True)
    title              = db.Column(db.String(200), nullable=False)
    author             = db.Column(db.String(100), nullable=False)
    isbn               = db.Column(db.String(20), unique=True, nullable=False)
    publisher          = db.Column(db.String(100))
    publish_year       = db.Column(db.Integer)
    quantity           = db.Column(db.Integer, default=1)
    available_quantity = db.Column(db.Integer, default=1)
    category_id        = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)
    issued_books       = db.relationship('IssuedBook', backref='book', lazy=True)
    requests           = db.relationship('BookRequest', backref='book', lazy=True)

    @property
    def is_available(self):
        return self.available_quantity > 0


class Member(db.Model):
    __tablename__ = 'members'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    email       = db.Column(db.String(100), unique=True, nullable=False)
    phone       = db.Column(db.String(15))
    department  = db.Column(db.String(100))
    join_date   = db.Column(db.DateTime, default=datetime.utcnow)
    status      = db.Column(db.Enum('active','inactive','suspended'), default='active')
    issued_books = db.relationship('IssuedBook', backref='member', lazy=True)
    requests     = db.relationship('BookRequest', backref='member', lazy=True)


class IssuedBook(db.Model):
    __tablename__ = 'issued_books'
    id          = db.Column(db.Integer, primary_key=True)
    book_id     = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id   = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    issue_date  = db.Column(db.DateTime, default=datetime.utcnow)
    due_date    = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    status      = db.Column(db.Enum('issued','returned','overdue'), default='issued')
    fine        = db.relationship('Fine', backref='issued_book', uselist=False, lazy=True)

    def calculate_fine(self):
        from config import Config
        if self.status == 'returned' and self.return_date:
            if self.return_date > self.due_date:
                return (self.return_date - self.due_date).days * Config.FINE_PER_DAY
        elif self.status in ['issued', 'overdue']:
            today = datetime.utcnow()
            if today > self.due_date:
                return (today - self.due_date).days * Config.FINE_PER_DAY
        return 0


class Fine(db.Model):
    __tablename__ = 'fines'
    id             = db.Column(db.Integer, primary_key=True)
    issued_book_id = db.Column(db.Integer, db.ForeignKey('issued_books.id'), nullable=False)
    amount         = db.Column(db.Float, default=0.0)
    paid           = db.Column(db.Boolean, default=False)
    paid_date      = db.Column(db.DateTime, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)


class BookRequest(db.Model):
    __tablename__ = 'book_requests'
    id           = db.Column(db.Integer, primary_key=True)
    book_id      = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id    = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    status       = db.Column(db.Enum('pending','approved','rejected'), default='pending')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at  = db.Column(db.DateTime, nullable=True)
    admin_note   = db.Column(db.String(255), nullable=True)