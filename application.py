import os
import requests
import stripe
from flask import Flask, session, render_template, request, flash , redirect,url_for, jsonify
from flask_session import Session
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import or_

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Stripe api
STRIPE_SECRET_KEY = 'sk_test_SIOaMkGy0iY4Q9ZzZb2E8da400zStCT5O8'
STRIPE_PUBLISHABLE_KEY = 'pk_test_jp5JvnlGk4kVHHEEfeeSDzCm007wAoW2lj'

stripe.api_key = STRIPE_SECRET_KEY

# Configure session to use filesystem
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set up database
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost'
db = SQLAlchemy(app)

class users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)

class booksdb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(5), nullable=False)

class reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(13), nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)

class orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(13), nullable=False)

@app.route('/', methods=['GET','POST'])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('index.html')


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.route('/register', methods=['POST', 'GET'])
def register():
    if session.get('logged_in'):
        return redirect (url_for('index'))

    else:
        if request.method == 'POST':
            # Create User Profile
            username = request.form.get("username")
            password = request.form.get("password")
            firstname = request.form.get("firstname")
            lastname = request.form.get("lastname")

            # Generate Password Hash
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            # Check if username already exists
            user_count = users.query.filter_by(username=username).count()
            if user_count > 0:
                flash('Username already taken!', 'danger')
                return redirect (url_for('register'))

            else:
                # Create User object
                new_user = users(username = username, password = password_hash, firstname = firstname, lastname = lastname)
                db.session.add(new_user)
                # Commit Changes
                db.session.commit()

                flash('Account successfully created!', 'success')

                # Redirect User to Login Page
                return redirect (url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('logged_in'):
        return redirect (url_for('index'))

    else:
        if request.method == 'POST':
            # Grab username and password
            username = request.form.get("username")
            password = request.form.get("password")

            session['user'] = username

            # Fetch user object
            user = users.query.filter_by(username=username).first()
            if user:
                password_check = bcrypt.check_password_hash(user.password, password)

                if password_check == False:
                    flash('Please check your username and password and try again', 'danger')
                else:
                    session['logged_in'] = True
                    return redirect (url_for('index'))
            else:
                flash('Please check your username and password and try again', 'danger')
    return render_template("login.html")


@app.route('/logout')
def logout():
    # Remove user from session
    session.pop('logged_in', None)
    session['user'] = []
    return redirect (url_for('login'))


@app.route('/account')
def account():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        # Get user information from database
        user_account = users.query.filter_by(username=session['user']).with_entities(users.username, users.firstname, users.lastname)
        return render_template("account.html", user_account=user_account)


@app.route('/books', methods=['GET','POST'])
def books():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        search = request.form.get("search")

        # Check if search is null, redirect to homepage
        if search is "":
            return redirect (url_for('index'))

        else:
            # Adding wildcard to previous variable
            search_query = "%{}%".format(search)
            books = booksdb.query.filter(or_(booksdb.author.like(search_query), booksdb.title.like(search_query), booksdb.isbn.like(search_query))).all()

            # Count number of books
            total_books = len(books)

            # Check if the user is logged out
            if not session.get('logged_in'):
                return redirect (url_for('login'))
            return render_template("books.html", books=books, total_books=total_books)

@app.route('/list', methods=['GET','POST'])
def list():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        # Search for books in database
        all_books = booksdb.query.all()

        # Check if the user is logged out
        if not session.get('logged_in'):
            return redirect (url_for('login'))
        return render_template("list.html", books=all_books)

@app.route('/addbook', methods=['GET','POST'])
def addbook():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('addbook.html')

@app.route('/add', methods=['GET','POST'])
def add():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        # Get details from user
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")
        year = request.form.get("year")

        # Check if ISBN is 13 digit
        if len(isbn) > 13:
            flash('ISBN cannot be more than 13 digit character', 'danger')

        else:
            # Check if book already exists in database
            book_object = booksdb.query.filter_by(isbn=isbn).count()
            if book_object > 0:
                flash("Book Already Exists!", 'warning')

            else:
                # Add book in database
                new_book = booksdb(isbn = isbn, title = title, author = author, year = year)
                db.session.add(new_book)
                # Commit Changes
                db.session.commit()

                flash("Book added successfully!", 'success')

        # Check if the user is logged out
        if not session.get('logged_in'):
            return redirect (url_for('login'))
        return render_template("addbook.html")

@app.route('/removebook', methods=['GET','POST'])
def removebook():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('removebook.html')

@app.route('/remove', methods=['GET','POST'])
def remove():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        # Get details from user
        isbn = request.form.get("isbn")

        # Check if book already exists in database
        book_count = booksdb.query.filter_by(isbn = isbn).count()
        if book_count == 0:
            flash("Book Doesn't Exists", 'warning')

        else:
            # Remove book in database
            books = booksdb.query.filter_by(isbn = isbn).first()
            db.session.delete(books)

            # Commit Changes
            db.session.commit()

            flash("Book deleted successfully!", 'success')

        # Check if the user is logged out
        if not session.get('logged_in'):
            return redirect (url_for('login'))
        return render_template("removebook.html")

@app.route('/search/<string:bookisbn>', methods=['GET', 'POST'])
def search(bookisbn):
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        # Get Current User ID
        user_id = users.query.filter_by(username = session["user"]).first()

        if request.method == "POST":
            # Get User Rating
            rating = request.form.get('options')

            # Get User Comment
            comment = request.form.get('comment')

            # Check if user has already submitted a review
            review_count = reviews.query.filter_by(user_id = user_id.user_id, isbn = bookisbn).count()
            if review_count > 0:
                flash("You have already reviewed this book!", 'warning')

            else:
                # Submit Review to SQL
                new_review = reviews(user_id = user_id.user_id, isbn =bookisbn, rate = rating, comment = comment)
                db.session.add(new_review)
                # Commit Changes
                db.session.commit()

                flash("Thank you for submitting your review!", 'success')

        books = booksdb.query.filter_by(isbn = bookisbn).first()

        # Total Reviews
        total_reviews = reviews.query.filter_by(isbn = bookisbn).count()

        # Average Reviews
        avg_ratings = db.session.query(func.avg(reviews.rate).label('average')).filter(reviews.isbn==bookisbn).scalar()

        try:
            # Get GoodReaders Reviews
            good_reads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oCYNGrqPgZeOJa3OS065Q", "isbns": bookisbn})

            # Parsing good_reads into JSON format
            good_reads_json = good_reads.json()['books'][0]

            good_reads_avg = good_reads_json['average_rating']
            good_reads_total = good_reads_json['ratings_count']
        except:
            good_reads_avg = '0.00'
            good_reads_total = 0

        # Display user Reviews
        user_reviews = users.query.outerjoin(reviews, users.user_id == reviews.user_id).with_entities(users.username, reviews.comment, reviews.rate).filter_by(isbn = bookisbn)

        return render_template("search.html", books=books, total_reviews=total_reviews, avg_ratings=avg_ratings, good_reads_avg=good_reads_avg, good_reads_total=good_reads_total, user_reviews=user_reviews)


@app.route('/api/<string:bookisbn>')
def api(bookisbn):
    books = booksdb.query.filter_by(isbn = bookisbn).first()

    # Show 404 if ISBN isn't available in the database
    if books is None:
        return jsonify({"error": "404 Book Not Found"})
    else:
        # Get the average ratings from reviews table
        review_count = reviews.query.filter_by(isbn = bookisbn).count()

    # Return the data user has requested
    return jsonify({
        "title": books.title,
        "author": books.author,
        "year": books.year,
        "isbn": books.isbn,
        "review_count": str(review_count)
        })

@app.route('/payment', methods=['POST'])
def payment_proceed():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        # Get details
        item = request.form.get("item")
        item_data = item.split(',')
        count = request.form.get("count")
        count_data = count.split(',')

        # Get Current User ID
        user_id = users.query.filter_by(username = session["user"]).first()
        for a in range(len(item_data)):
            for b in range(int(count_data[a])):
                new_order = orders(isbn = item_data[a], user_id = user_id.user_id)
                db.session.add(new_order)
        # Commit Changes
        db.session.commit()
    flash('Payment successful!', 'success')
    return render_template('index.html')

@app.route('/order', methods=['GET','POST'])
def order():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        # Get Current User ID
        user_id = users.query.filter_by(username = session["user"]).first()
        # get all order
        all_orders = orders.query.filter_by(user_id = user_id.user_id).join(
            users, orders.user_id == users.user_id
        ).join(
            booksdb, orders.isbn == booksdb.isbn
        ).with_entities(
            users.username, booksdb.title
        )
        return render_template("order.html", all_orders=all_orders)
