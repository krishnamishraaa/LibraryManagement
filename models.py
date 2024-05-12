from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db= SQLAlchemy()


class User(db.Model): 
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name = db.Column(db.String, unique= True, nullable= False)
    email = db.Column(db.String, unique=True)
    passwordhash = db.Column(db.String(255))
    name = db.Column(db.String)
    req_count= db.Column(db.Integer, default=0)
    total_req = db.Column(db.Integer, autoincrement=True)
    is_admin = db.Column(db.Boolean, nullable= False, default= False)
    is_premium = db.Column(db.Boolean, nullable= False, default= False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.passwordhash = generate_password_hash(password)
    
    def checkpassword(self, password):
        return check_password_hash(self.passwordhash, password)


class Section(db.Model):
    __tablename__ = "section"
    section_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    section_name= db.Column(db.String, unique = True)
    section_date_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    section_description = db.Column(db.String)
    section_ratings = db.Column(db.String)
    section_book_count= db.Column(db.Integer)
    
   
    # Relationship for calculating Average 
    def average_rating(self):
        # Query all books in this section
        books_in_section = Book.query.filter_by(book_sec=self.section_id).all()
        book_count = len(books_in_section)

        # Book Count
        self.section_book_count = book_count

        total_rating = sum(book.book_rating for book in books_in_section if book.book_rating is not None)
        if book_count != 0:
            average_rating = total_rating / book_count
        else:
            average_rating = 0
        
        #Rating Update
        self.section_ratings = average_rating


class Book(db.Model):
    __tablename__ = "book"
    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_name = db.Column(db.String, nullable=False)
    book_content = db.Column(db.String, nullable=False)
    book_author = db.Column(db.String)
    book_image = db.Column(db.String)
    book_sec = db.Column(db.Integer, db.ForeignKey('section.section_id'), nullable=False)
    book_rating = db.Column(db.Float, default=0.0)
    book_views = db.Column(db.Integer, default=0)
    is_premium = db.Column(db.Boolean, nullable= False, default= False)
    sec_name = db.Column(db.String,  nullable=False)

    feedback = db.relationship("Feedback", backref="book")

    @property
    def book_rating(self):
        
        feedback_ratings = [feedback.rating for feedback in self.feedback]
        if feedback_ratings:
            return sum(feedback_ratings) / len(feedback_ratings)
        else:
            return 0.0


class Feedback(db.Model):
    __tablename__ = "feedback"
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    rating = db.Column(db.Float, default=0.0)
    comment = db.Column(db.String)
    time = db.Column(db.DateTime, nullable=False)

class Issue(db.Model):
    __tablename__ = "issue"
    transaction_id = db.Column(db.Integer, primary_key= True, autoincrement=True, nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default= datetime.utcnow)
    issue_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    book_id = db.Column(db.String, db.ForeignKey('book.book_id'))
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    issue_link = db.Column(db.String)
    link_active = db.Column(db.Boolean , default=False)

    book = db.relationship('Book', backref=db.backref('issues', lazy=False))
    

    def auto_return(self):
        if self.link_active and self.return_date is None and (datetime.utcnow() - self.issue_date).days > 7:
            self.link_active = False
            self.issue_link=""

def initialize_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()    
        admin = User.query.filter_by(user_name='admin').first()
        if not admin:
            admin = User(user_name ='admin', password = 'admin', name = 'admin', is_admin = True)
            db.session.add(admin)
            db.session.commit()
        
            
        premium = User.query.filter_by(user_name='krishna').first()
        if not premium:
                prem = User(user_name ='krishna', password = 'krishna', name = 'Krishna', is_admin = True, is_premium = True)
                db.session.add(prem)
                db.session.commit()