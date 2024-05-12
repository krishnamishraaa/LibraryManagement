<b>Library Management System</b>
<br>
<br>It is a multi-user app (one required librarian and other general users/students)
    Used for issuing e-books to users
<br>User can request, read, return e-books
<br>Librarian can add new sections/e-books, issue/revoke access for a book.
<br>Each Section may have
    ID
    Name
    Date created
    Description
<br>Each book will have
    ID
    Name
    Content
    Author(s)
    Date issued
    Return date.
Every section can have a number of books
<br> System will automatically show recently added sections/books or based on certain rating


Refer to the wireframe attached;
<br> Library Management

<br>Core Functionality
  Base requirements:
    Librarian’s Dashboard
    General User Profile
    Section Management
    Book Management
    Search functionality for section/e-books 

<br>Core - Librarian and User Login
    Form for username and password for user
    Separate form for librarian login for simplicity
    You can either use a proper login framework, or just use a simple HTML form with username and password - we are not concerned with how secure the login or the app is.
    Suitable model for user (Model that stores the type of users and differentiates them correctly based on their role)

<br>Core - General User functionalities
    Login/Register
    View all the existing Sections/e-books 
    Request/Return Books (content)
    A user can request for a maximum of 5 e-books 
    A user can access a book for a specific period of time (say N hours/days/weeks).
    For e.g. if N = 7 days, user can return a book before 7 days. If he/she fails to do so, the access for that will be automatically revoked after 7 days.
    User can give feedback for an e-book

<br>Core - Librarian functionalities
    Issue one or multiple e-book(s) to a user
    Revoke access for one or multiple e-book(s) from a user
    Storage should handle multiple languages - usually UTF-8 encoding is sufficient for this
    Edit an existing section/e-book
    Change content, author name,  no. of pages/volume etc.
    Remove an existing section/e-book
    Assign a book to a particular section
    A librarian can monitor current status of each e-book and the user it is issued to
    Available e-books in the Library

<br>Core - Search for e-books/sections
    Ability to search for a particular section.
    Ability to search e-books based on section, author etc.

Recommended
    Download e-books as PDF for a price 
    APIs for interaction with sections and books
    CRUD on e-books/sections
    Additional APIs for getting the creating graphs for librarian dashboard
    <br>Validation
        All form inputs fields - text, numbers, dates etc. with suitable messages
        Backend validation before storing / selecting from database

Optional
    Styling and Aesthetics
    Proper login system
    Subscriptions or paid versions of the app, become author etc 
    Ability of app to read books for a user (text-to-speech)

