# Project 1

# HOWTO
1. Go to the project Directory
2. Run python
3. Enter `from application import db`
4. Run `db.create_all()`
5. Exit Python by running `exit()`
6. You can optionally run import.py script to import books.csv `python import.py`. Please make sure to change the database string.
7. Run `export FLASK_APP=application.py`
8. Run `flask run`

## Testing Stripe
You can use test credit card numbers following directions from https://stripe.com/docs/testing to place an order.

## Index.html
As soon as the user logs in, they will be displayed with the home page. Home page has search bar that will allow user to search for books by title, author or ISBN. User can use partial keywords to display all matching results. The displayed result can be sorted, searched even further and only displayed 10 items per page which can be changed from the dropdown menu.
 -> Account Page shows account information.
 -> Cart shows number of items in the cart. User can pay for books rental from here.
 -> Clear cart will remove all items from the Cart

## Account.html
This page displays user account information (username, first name, and last name).

## Books.html
This page provides the list of books matching user's query at the home page. If the query is invalid, or if the book cannot be found in the database, the page will display with an error. Successful query result will display title, book name, author name, and year. Users will have an option to click on `details` link to show more details about that specific book. User can click on the cart icon to rent books.

## Addbook.html
Users can add new book.

## Removebook.html
Users can remove any book.

## Orders.html
Shows all books ordered by specific user.

## List.html
Displays all books in the database. The displayed result can be sorted, searched even further and only displayed 10 items per page which can be changed from the dropdown menu.

## Layout.html
Layout is the template page that populates navigation bar, cart and header to each page.

## Login.html
Users will have to provide username and password to login. Incorrect credentials will display an error.

## Register.html
Users will be able to register with a unique username, password, first name and last name.

## Search.html
This page will display details about a specific book. The result displays goodreads total ratings, average ratings, user ratings and comments.

## 404.html
If user browse to an incorrect URL, they will be displayed with a custom 404 error.

## import.csv
This script will allow user to import books.csv to database set with "DATABASE_URL" environmental variable.

## application.py
This file is the main logic behind this project. The file contains routes to all pages and how to handle user requests when they come in.
