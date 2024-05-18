from flask import Flask , render_template, flash, request, redirect, url_for, session
from functools import wraps
from sqlalchemy import func , desc
from sqlalchemy.exc import IntegrityError
import matplotlib.pyplot as plt
from datetime import datetime
from models import *
from app import app
from flask import request, redirect, url_for

#CORE  & COMMON Functionalities ...................................................................


def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to login to continue")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to login to continue")
            return redirect(url_for('login'))
        user=User.query.get(session['user_id'])
        if not user.is_admin:
            flash("You are not authorized to view this page")
            return render_template('home.html',user= user)
        return func(*args, **kwargs)
    return inner

# def premium_required(func):
#     @wraps(func)
#     def inner(*args, **kwargs):
#         if 'user_id' not in session:
#             flash("You need to login to continue")
#             return redirect(url_for('login'))
#         user=User.query.get(session['user_id'])
#         if not (user.is_admin or user.is_premium):
#             flash("You are not a Premium Member, Please signup for membership")
#             return redirect(url_for('edit_profile'))
#         return func(*args, **kwargs)
#     return inner

@app.route("/readme")
def readme():
    return render_template('readme.md')
@app.route("/previous")
def previous():
    return render_template('previouspage.html')

@app.route("/book_issued/<int:section_id>", methods= ["GET","POST"])
@auth_required
def book_issued(section_id):
    books= Book.query.filter_by(book_sec=section_id).all()
    return render_template('book_issued.html',user= User.query.get(session['user_id']), books=books)

#  LOGIN <> HOME <> ROOT <> LOGOUT
@app.route("/", methods= ['GET','POST'])
@auth_required
def index():
    return render_template('login.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user_name= request.form.get('username')
        password = request. form.get('password')
# Checking for Blank Entries
    
        if user_name== ' ' or password == ' ':
            flash("User Id or Password Cant be blank")
    # Checking user_name in database
            
        user= User.query.filter_by(user_name=user_name).first()
        if not user:
            flash("User Does Not Exist!")
            return redirect (url_for('login'))
        if not user.checkpassword(password):
            flash('Incorrect Password')
            return redirect (url_for('login'))
    # Check Admin Credentianls
        session['user_id']= user.id
        session['user_name']= user.user_name
        session['is_admin']= user.is_admin
        
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route("/admin")
def admin():
    return render_template('admin.html')
    
@app.route("/home", methods= ['GET','POST'])
@auth_required
def home():
    current_date=datetime.utcnow()
    user=User.query.get(session['user_id'])
    pendings= Issue.query.filter(Issue.issue_date.is_(None)).all()
    issued= Issue.query.filter(Issue.issue_date !=None).all()
    parameter= request.args.get('parameter')
    search= request.args.get('search')
    secs= Section.query.all()
    for sec in secs:
        sec.average_rating() #this one updates book Count & Ratings of section
    db.session.commit()

    
    if not parameter or not search:
        return render_template('home.html',user=user,section= Section.query.all(), pendings=pendings, issued=issued, current_date=current_date)
   

    if parameter == 'section':
        sect = Section.query.filter(Section.section_name.ilike(f'%{search}%')).all()
        pendings = Issue.query.join(Book).join(Section).filter(Issue.issue_date.is_(None), Section.section_name.ilike(f"%{search}%")).all()
        issued = Issue.query.join(Book).join(Section).filter(Issue.issue_date != None, Section.section_name.ilike(f"%{search}%")).all()
        return render_template('home.html', user=user, section=sect, pendings=pendings, issued=issued, current_date=current_date)
    
    if parameter =='user':
        query = Issue.query.join(User, Issue.user_id == User.id)
        pendings = query.filter(Issue.issue_date.is_(None), User.user_name.ilike(f"%{search}%")).all()
    
        issued = query.filter(Issue.issue_date != None, User.user_name.ilike(f"%{search}%")).all()
        return render_template('home.html',user=user,section= Section.query.all(), pendings=pendings, issued=issued,current_date=current_date)

    if parameter == 'author':
        books= Book.query.filter(Book.book_author.ilike(f"%{search}%")).all()
        
        section_ids = [book.book_sec for book in books]
        
        sect = Section.query.filter(Section.section_id.in_(section_ids)).all()
        
        return render_template('home.html',user=user,section=sect,current_date=current_date)
    
    if parameter =='book':
        sect=Section.query.all()
        books=Book.query.filter(Book.book_name.ilike(f"%{search}%")).all()
        pendings = Issue.query.join(Book).filter(Issue.issue_date.is_(None), Book.book_name.ilike(f"%{search}%")).all()
        issued = Issue.query.join(Book).filter(Issue.issue_date != None, Book.book_name.ilike(f"%{search}%")).all()
        return render_template('home.html', user=user, section=sect, pendings=pendings, issued=issued,current_date=current_date)


    return render_template('home.html',user=user,section= Section.query.all(), pendings=pendings, issued=issued, books=books, current_date=current_date)
    
@app.route("/logout")
@auth_required
def logout():
    session.pop('user_id', None)
    
    return render_template('login.html')

# REGISTER- & EDIT PROFILE-------------------------------------

@app.route("/register", methods= ['GET','POST'])
def register():

    if request.method== 'POST':
        user_name= request.form.get('username')
        password = request. form.get('password')
        name= request.form.get('name')
        email= request. form.get('email')
#  Checking Blank Fields
        if user_name == " " or password == " ":
            flash ('Mandatory Fields cant be empty')
            return redirect (url_for('register'))
#  Checking Existing User Name
        if User.query.filter_by(user_name=user_name).first():
            flash("User_name is taken, please choose another user name")
            return redirect (url_for('register'))
#  Adding Values in Database
        user = User(user_name= user_name, password= password, name= name, email= email)
        db.session.add(user)
        db.session.commit()
        flash("User Registered successfully, Please Log In to Continue")
        return redirect (url_for('login'))
    
    return render_template('register.html')


@app.route("/edit_profile", methods= ['GET','POST'])
@auth_required
def edit_profile():
    user=User.query.get(session['user_id'])
    if request.method== 'POST':
        user_name= request.form.get('username')
        password = request. form.get('password')
        name= request.form.get('name')
        email= request. form.get('email')
        is_premium= request.form.get('premium')
        
        if is_premium == 'None':
            premium=False
        else:
            premium=True
       
        if user_name == " " or password == " ":
            flash ('Mandatory Fields cant be empty')
            return redirect (url_for('edit_profile'))
        
        user.name = name
        user.email = email
        user.is_premium = premium
        db.session.commit()

        flash(f"User Edited successfully, your Premium status is: {user.is_premium}")
        return redirect(url_for('home', user=user))
    
    return render_template('edit_profile.html',user=user)


#  STATISTICS STATS   
@app.route("/stats")
@auth_required
def stats():
    user=User.query.get(session['user_id'])
    book_count= Book.query.count()
    author_count= Book.query.distinct(Book.book_author).count()
    transaction_count=Issue.query.filter(Issue.return_date== None).count()
    user_count = User.query.count()
    engmnt =[transaction_count, user_count, book_count,author_count,]
    current_date=datetime.utcnow()
    parameter= request.args.get('parameter')
    if not parameter:
        parameter='section'


    # Section Chart & Section Table
    if parameter=='section' :
        sec_book_counts = db.session.query(Section.section_name, func.count(Book.book_id), Section.section_ratings, Section.section_date_created).join(Book,Book.sec_name==Section.section_name).group_by(Section.section_name).all()
        book_counts=[section[1] for section in sec_book_counts]
        section_names=[section[0] for section in sec_book_counts]
        plt.figure(figsize=(6,6))
        numbers= book_counts
        books= section_names    
        fig,ax = plt.subplots()
        ax.pie(numbers, labels=books,  autopct='%1.1f%%') #hatch=[ 'oO', 'O.O', '.||.'],
        fig.savefig('static/section.png')
        
        return render_template("stats.html",engmnt=engmnt, user=user, parameter=parameter,x=sec_book_counts, current_date=current_date)

    
    # Book Charts & Tables
    if parameter == 'book':
        pop_books= Book.query.order_by(desc(Book.book_views)).limit(10)
        book_name=[book.book_name for book in pop_books ]
        book_views=[book.book_views for book in pop_books]
        book_rating=[book.book_rating for book in pop_books]
        fig, ax = plt.subplots(figsize=(10,6))
        bar_container = ax.bar(book_name, book_views, color='yellow')
        ax.set(ylabel='Views', title='Top 10 Books')
        ax.bar_label(bar_container, fmt='{:,.0f}')
        plt.setp(ax.get_xticklabels(), rotation=10, ha='right')
        plt.savefig('static/book.png')
        return render_template("stats.html",engmnt=engmnt, user=user, parameter=parameter,x=pop_books)




    if parameter == 'author':
        x='author'
        top_author= db.session.query(Book.book_author, func.count(Book.book_id).label('book_wrote')).group_by(Book.book_author).order_by(desc('book_wrote')).limit(10)
        author_names = [author.book_author for author in top_author]
        books_wrote = [author.book_wrote for author in top_author]

        fig, ax = plt.subplots(figsize=(10, 6))
        bar_container = ax.bar(author_names, books_wrote, color='skyblue')
        ax.set(ylabel='Books Authored', title='Top Writers')
        ax.bar_label(bar_container, fmt='{:,.0f}')
        plt.setp(ax.get_xticklabels(), rotation=10, ha='right')
        plt.savefig('static/author.png')
        return render_template("stats.html",engmnt=engmnt, user=user, parameter=parameter,x=top_author)


    if parameter == 'user':
        x='user'
        top_users = db.session.query(Issue.user_id, func.count(Issue.transaction_id).label('books_read')).group_by(Issue.user_id).order_by(desc('books_read')).limit(15)
        
        user_ids = [user[0] for user in top_users]
        books_read = [user[1] for user in top_users]
        user_names = [User.query.get(user_id).user_name for user_id in user_ids]
       
        fig, ax = plt.subplots(figsize=(10, 6))
        bar_container = ax.bar(user_names, books_read , color='orange')
        ax.set(ylabel='Books Read', title='Top Active Users')
        
        ax.bar_label(bar_container, fmt='{:,.0f}')
       
        plt.setp(ax.get_xticklabels(), rotation=10, ha='right')

        plt.savefig('static/user.png')
        return render_template("stats.html",engmnt=engmnt, user=user, parameter=parameter,x=top_users, y=user_names)


    return render_template("stats.html",engmnt=engmnt, user=user, parameter=parameter)


@app.route("/admin_stats")
@admin_required
def admin_stats():
    return redirect(url_for('stats'))

# SUMMARY ADDITIONAL LINKS 
@app.route("/book_summary/<int:id>")
@auth_required
def book_summary(id):
    buk= Book.query.filter_by(book_id=id).first()
    buk.book_views+=1
    db.session.commit()

    return render_template('book_summary.html',user=User.query.get(session['user_id']) , book= buk,path=buk.book_content)

# SEARCH QUERY  
@app.route("/search_issued", methods = ['POST'])
@auth_required
def search_issued():
    return 'This feature Coming Soon'

#ADMIN Related ...................................................................

# =========== SECTION ====================
@app.route("/add_section", methods= ['GET','POST'])
@admin_required
def add_section():
    if request.method == 'GET':
        return render_template("add_section.html")
    else:
        section_name= request.form.get('title')
        section_description = request.form.get('description')
        sect= Section(section_name=section_name,section_description=section_description)
        db.session.add(sect)
        db.session.commit()
        flash("Section Added Succesfully")
        return render_template("lib_book_sec.html",user=User.query.get(session['user_id']), section = Section.query.all())

@app.route("/edit_section/<int:section_id>", methods= ['GET','POST'])
@admin_required
def edit_section(section_id):
    sect= Section.query.get(section_id)
    if request.method == 'GET':
        return render_template("edit_section.html", section=sect)
    else:
        section_name= request.form.get('title')
        section_description = request.form.get('description')

        if section_name == " " or section_description == " ":
            flash ('Mandatory Fields cant be empty')
            return redirect (url_for('/edit_section', section_id=section_id))

        sect.section_name=section_name
        sect.section_description=section_description
        db.session.commit()
        flash("Section Updated Succesfully")
        return render_template("lib_book_sec.html",user=User.query.get(session['user_id']), section = Section.query.all())    

@app.route("/edit_section/<int:section_id>/delete", methods=["POST"])
@admin_required
def delete_section(section_id):
    #Query the Section & Books in section
    sect = Section.query.get_or_404(section_id)
    buk= Book.query.get(section_id)
    if buk:
        flash(f"Can't delete section {sect.section_name}, Please transfer books to appropriate section first")
        return redirect(url_for('lib_book_sec'))

    db.session.delete(sect)
    db.session.commit()

    flash(f"Section deleted successfully", "success") 
    return redirect(url_for("lib_book_sec"))

# ================== BOOK ===================================
@app.route("/add_book/<int:section_id>", methods= ['GET', 'POST'])
@admin_required
def add_book(section_id):
    section = Section.query.get(section_id)
    if request.method == 'GET':
        return render_template("add_book.html", section_id = section_id)
    else:
        book_name= request.form.get('title')
        book_author= request.form.get('author')
        book_content = request.form.get('link')
        book_sec = request.form.get('section')
        book_image= request.form.get('image')
        sec_name= section.section_name
        buk= Book(book_name=book_name,book_author=book_author,book_content=book_content,book_sec=book_sec, book_image=book_image, sec_name=sec_name)
        db.session.add(buk)
        db.session.commit()
        flash("Book Added Succesfully")
        return render_template("lib_book_sec.html",user= User.query.get(session['user_id']), section=Section.query.all())

@app.route("/edit_book/<int:book_id>", methods= ['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book= Book.query.get(book_id)
    sect= book.book_sec
    section= Section.query.all()
    if request.method == 'GET':
        return render_template("edit_book.html", book= book, sections=section)
    else:
        book_name= request.form.get('title')
        book_author= request.form.get('author')
        book_content = request.form.get('link')
        book_sec = request.form.get('section')
        book_image= request.form.get('image')
        
        if book_name ==" " or book_author== "" or book_content ==" " or book_sec==" ":
            flash('Mandatory fields cant be empty, please fill them')
            return redirect (url_for('edit_book', book_id=book.book_id))
        sect=Section.query.get(book_sec)
        if not sect:
            flash(f"Section{book_sec} is not available, Please choose another Section")
            return redirect (url_for('edit_book', book_id=book.book_id))

        book.book_name= book_name
        book.book_author=book_author
        book.book_content=book_content
        book.book_sec = book_sec
        book.book_image=book_image
        db.session.commit()
        flash("Book Updated Succesfully")
        return render_template("lib_book_sec.html",user= User.query.get(session['user_id']), section=Section.query.all())

@app.route("/edit_book/<int:book_id>/delete", methods=["POST"])
@admin_required
def delete_book(book_id):
    #Query the book
    book = Book.query.get_or_404(book_id)
    x=book.book_name

    # Delete the book
    db.session.delete(book)
    db.session.commit()

    flash(f"Book {x} deleted successfully", "success") 
    return redirect(url_for("lib_book_sec"))

@app.route('/lib_book_sec', methods= ['GET','POST'])
@admin_required
def lib_book_sec():
    user=User.query.get(session['user_id'])
    section = Section.query.all()
    parameter= request.args.get('parameter')
    search= request.args.get('search')

    if parameter == 'section':
        section= Section.query.filter(Section.section_name.ilike(f"%{search}%")).all()
    
        return render_template('lib_book_sec.html', user=user, section= section)
    return render_template('lib_book_sec.html', user=user, section= section)

#  APPROVE & REVOKE ------------------------------

@app.route("/approve_book/<int:user_id>/<int:book_id>")
@admin_required
def approve(user_id,book_id):
    book=Book.query.get(book_id)
    appr = Issue.query.filter_by(book_id=book_id,user_id=user_id).order_by(Issue.transaction_id.desc()).first()
    appr.issue_date=datetime.utcnow()
    appr.issue_link=book.book_content
    appr.link_active=True
    db.session.commit()
    flash("Book Granted Succefully")
    return redirect(url_for('home'))

@app.route("/revoke/<int:user_id>/<int:book_id>")
@admin_required
def revoke(user_id,book_id):
    revo = Issue.query.filter_by(book_id=book_id,user_id=user_id).first()
    revo.return_date=datetime.utcnow()
    revo.issue_link=None
    revo.link_active=False
    db.session.commit()
    flash(f"Book: {book_id} Revoked from user: {user_id}")
    return redirect(url_for('home'))

# Rejection will have same issue time & return time 

@app.route("/reject/<int:user_id>/<int:book_id>")
@admin_required
def reject(user_id,book_id):
    reject = Issue.query.filter_by(book_id=book_id,user_id=user_id).order_by(Issue.transaction_id.desc()).first()
    reject.issue_date=datetime.utcnow()
    reject.return_date=datetime.utcnow()
    reject.issue_link=None
    reject.link_active=False
    db.session.commit()
    flash(f"Book: {book_id} Rejected for: {user_id}")
    return redirect(url_for('home'))


#---------------------USER  Related ..----.....................................

# PREMIUM --------------------------
# @app.route("/premium/<int:book_id>")
# @premium_required
# def premium(book_id):
#     user= User.query.get(session['user_id'])
#     return render_template("premium.html", book = Book.query.get(book_id), user=user)

# USERHOME USERREQ REQ & MYBOOK----------------------------
@app.route("/UserReq")
@auth_required
def UserReq():
    
    user=User.query.get(session['user_id'])
    user_limit = Issue.query.filter(Issue.user_id == user.id, Issue.return_date == None).count()
    issued_books_ids = [issue.book_id for issue in Issue.query.filter_by(user_id=user.id, return_date=None).all()]
    books = Book.query.filter(Book.book_id.notin_(issued_books_ids)).all()

    parameter= request.args.get('parameter')
    search= request.args.get('search')

    if not parameter or not search:
        return render_template('UserReq.html', user=user,books=books,user_limit=user_limit)

    if parameter =='section':
        books = Book.query.filter(~Book.book_id.in_(issued_books_ids),Book.sec_name.ilike(f"%{search}%")).all()
        return render_template("UserReq.html",user=user,books=books, user_limit=user_limit)


    if parameter == 'author':
        books = Book.query.filter(~Book.book_id.in_(issued_books_ids),Book.book_author.ilike(f"%{search}%")).all()
        return render_template("UserReq.html",user=user,books=books, user_limit=user_limit)
    
    if parameter =='book':
        books = Book.query.filter(~Book.book_id.in_(issued_books_ids),Book.book_name.ilike(f"%{search}%")).all()
        return render_template("UserReq.html",user=user,books=books, user_limit=user_limit)

    return render_template("UserReq.html",user=user,books=books, user_limit=user_limit)

@app.route("/my_book")
@auth_required
def my_book():
    
    user=User.query.get(session['user_id'])
    current_book= Issue.query.filter(Issue.user_id==user.id, Issue.link_active==True).all()
    completed_book= Issue.query.filter(Issue.user_id==user.id, Issue.return_date!=None).all()
    parameter= request.args.get('parameter')
    search= request.args.get('search')

    # AUTO RETURN ------------------------
    issues = Issue.query.filter(Issue.link_active == True, Issue.return_date != None).all()
    for issue in issues:
        issue.auto_return()

    if not parameter or not search:
        return render_template("my_books.html",user=user, current_books=current_book, completed_books=completed_book)


    if parameter =='section':
        completed_book = [issue for issue in completed_book if search.lower() in issue.book.sec_name.lower()]
        return render_template("my_books.html",user=user, current_books=current_book, completed_books=completed_book)


    if parameter == 'author':
        completed_book = [issue for issue in completed_book if search.lower() in issue.book.book_author.lower()]
        return render_template("my_books.html",user=user, current_books=current_book, completed_books=completed_book)
    
    if parameter =='book':
        completed_book = [issue for issue in completed_book if search.lower() in issue.book.book_name.lower()]
        return render_template("my_books.html",user=user, current_books=current_book, completed_books=completed_book)
    return render_template("my_books.html",user=user, current_books=current_book, completed_books=completed_book)

#  ISSUE RETURN BOOK Request
@app.route("/issue_book/<int:book_id>/<int:user_id>")
@auth_required
def issue_book(book_id,user_id):
    user=User.query.get(session['user_id'])
    book=Book.query.get(book_id)
    user_limit=Issue.query.filter(Issue.user_id==user_id , Issue.return_date==None).count()
    

    if user_limit>5 and user.is_premium == False:
        flash("User Limit Reached, you cant issue more than 5 Books.Return Earlier Books first")
        flash("Signup for our Premium Membership to enjoy unlimited Books")
        return redirect(url_for('edit_profile'))
    elif user.is_premium:
        issue_date=datetime.utcnow()
        issue_link=book.book_content
        link_active=True
        
        this_issue=Issue(
        book_id=book_id,
        user_id=user_id, issue_date=issue_date,issue_link=issue_link,link_active=link_active)
        db.session.add(this_issue)
        db.session.commit()
        book=Book.query.get(book_id)
        flash(f"{book.book_name} added in your list")
        return redirect(url_for('UserReq'))

    else:
        this_issue=Issue(
        book_id=book_id,
        user_id=user_id)
        db.session.add(this_issue)
        db.session.commit()
        book=Book.query.get(book_id)
        flash(f"request for {book.book_name} placed successfully")
        return redirect(url_for('UserReq'))

@app.route("/return_book/<int:book_id>")
@auth_required
def return_book(book_id):
    user_id=session.get('user_id')
    rr= Issue.query.filter(Issue.book_id==book_id, Issue.user_id==user_id).order_by(Issue.transaction_id.desc()).first()
    
    if rr:
        rr.return_date = datetime.utcnow()
        rr.issue_link= None
        rr.link_active= False 
        db.session.commit()
        fdbk= Feedback.query.filter_by(user_id=user_id,book_id=book_id).first()
        if fdbk:
            flash("Returned succefully")
            return redirect(url_for('my_book'))
        flash(f"Returned Successfully, Please share your Feedback for {rr.book.book_name}")
    else:
        flash("Issue Not Found")
    return redirect(url_for('feedback', user_id=user_id,book_id=book_id))

@app.route("/feedback/<int:user_id>/<int:book_id>", methods=['GET','POST'])
@auth_required
def feedback(user_id, book_id):

    if request.method =='POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        time = datetime.utcnow()
        try:
            fdbk=Feedback(rating = rating, comment= comment, time= time, book_id=book_id, user_id=user_id )
            db.session.add(fdbk)
            db.session.commit()
            flash("We appreciate your feedback!") 
        except IntegrityError as e:
            if "unique constraint" in str(e):
                flash("You already submitted feedback for this book")
            else:
                flash(f"IntegrityError occurred:{e}")
            db.session.rollback()
        except Exception as e:
            flash(f"An error occurred: {e}")
            db.session.rollback()
        
        return redirect(url_for('my_book'))
    return render_template('feedback.html', user_id=user_id, book_id=book_id)






