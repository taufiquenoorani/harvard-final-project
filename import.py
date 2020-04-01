import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session
from flask_session import Session
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Set up database
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost'
db = SQLAlchemy(app)
from application import booksdb

with open('books.csv', 'r') as books:
    read_books = csv.reader(books)

    # Skip the header
    next(read_books)

    for isbn, title, author, year in read_books:
        new_book = booksdb(isbn = isbn, title = title, author = author, year = year)
        db.session.add(new_book)
    # Commit Changes
    db.session.commit()
