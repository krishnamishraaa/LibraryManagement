from flask_restful import Resource , fields , marshal_with , reqparse 
from models import *
from flask import jsonify
from sqlalchemy import desc

output_fields_section = {
    "section_id" : fields.Integer,
    "section_name" : fields.String,
    "section_description" : fields.String,
    "section_ratings" : fields.Float,
    "section_book_count" : fields.Integer
}

output_fields_book = {
    "book_id" : fields.Integer,
    "book_name" : fields.String,
    "book_author" : fields.String,
    "is_premium" : fields.Boolean
}



class Section_api(Resource):
    @marshal_with(output_fields_section)
    
    def get(self,section_id):
   
        sec= Section.query.get(section_id)
        if sec:
            return sec
        return {} , 404
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('section_name' , type=str, required=True)
        parser.add_argument('section_description', type=str, required=True)
        args= parser.parse_args()
        section_name=args['section_name']
        section_description = args['section_description']
        sect= Section(section_name=section_name,section_description=section_description)
        x=section_name
        
        # Check that Section Names is not Existing already
        unique_chk = Section.query.filter_by(section_name=section_name).first()
        
        if unique_chk:
             return {'message': 'Section with the same name already exists, Choose another'}, 400

        db.session.add(sect)
        db.session.commit()
        section_id=Section.query.filter_by(section_name=x).first_or_404()
        return {'message':f'Section Registered Successfully with section id:{section_id.section_id}'}, 201
# PUT
    def put(self,section_id):
        parser = reqparse.RequestParser()
        parser.add_argument('section_name', type=str, required=True)
        parser.add_argument('section_description', type=str, required=True)
        args = parser.parse_args()
        new_section_name = args['section_name']
        new_section_description = args['section_description']

        section = Section.query.get(section_id)
        if not section:
            return {'message': 'Section not found'}, 404
        
        if new_section_name != section.section_name:
            existing_section = Section.query.filter_by(section_name=new_section_name).first()
            if existing_section:
                return {'message': 'Section with the same name already exists. Choose another.'}, 400

        section.section_name = new_section_name
        section.section_description = new_section_description
        db.session.commit()
        return {'message': f'Section {section_id} updated successfully'}, 200
    
class Book_api(Resource):
   
    def post(self,section_id):
        parser = reqparse.RequestParser()
        parser.add_argument('book_link', type=str, required=True)
        parser.add_argument('book_name', type=str, required=True)
        parser.add_argument('author', type=str, required=True)
        parser.add_argument('is_premium', type=bool, required=True)
        args = parser.parse_args()

        book_link = args['book_link']
        book_name = args['book_name']
        author = args['author']
        is_premium = args['is_premium']

        section = Section.query.get(section_id)
        if not section:
            return {'message': 'Section not found'}, 404

        book = Book(book_content=book_link, book_name=book_name, book_author=author, is_premium=is_premium, book_sec=section_id)
        db.session.add(book)
        db.session.commit()

        return {'message': 'Book added successfully'}, 201
    
    def put(self, section_id, book_id):
        parser = reqparse.RequestParser()
        parser.add_argument('book_link', type=str)
        parser.add_argument('book_name', type=str)
        parser.add_argument('author', type=str)
        parser.add_argument('is_premium', type=bool)
        args = parser.parse_args()

        book_content = args.get('book_link')
        book_name = args.get('book_name')
        book_author = args.get('author')
        is_premium = args.get('is_premium')

        section = Section.query.get(section_id)
        if not section:
            return {'message': 'Section not found'}, 404

        book = Book.query.filter_by(book_id=book_id, book_sec=section_id).first()
        if not book:
            return {'message': 'Book not found'}, 404

        if book_content:
            book.book_content = book_content
        if book_name:
            book.book_name = book_name
        if book_author:
            book.book_author = book_author
        if is_premium is not None:
            book.is_premium = is_premium

        db.session.commit()

        return {'message': 'Book updated successfully'}, 200
    
    def delete(self, section_id, book_id):
        
        book = Book.query.filter(Book.book_id==book_id, Book.book_sec==section_id).first()

        if not book:
            return {'message': 'Book not found'}, 404
        
        db.session.delete(book)
        db.session.commit()
        return {'message': 'Book Deleted from Database'}, 200

class Graph_api(Resource):
    def get(self, parameter):
        data = None
        if parameter == 'section':
            sec_book_counts = db.session.query(Section.section_name, func.count(Book.book_id), Section.section_ratings, Section.section_date_created).join(Book, Book.sec_name == Section.section_name).group_by(Section.section_name).all()
            data = [{'section_name': section[0], 'book_count': section[1], 'section_ratings': section[2], 'section_date_created': section[3]} for section in sec_book_counts]

        elif parameter == 'book':
            pop_books = Book.query.order_by(desc(Book.book_views)).limit(10)
            data = [{'book_name': book.book_name, 'book_views': book.book_views, 'book_rating': book.book_rating} for book in pop_books]

        elif parameter == 'author':
            top_author = db.session.query(Book.book_author, func.count(Book.book_id).label('book_wrote')).group_by(Book.book_author).order_by(desc('book_wrote')).limit(10)
            data = [{'author_name': author.book_author, 'books_wrote': author.book_wrote} for author in top_author]

        elif parameter == 'user':
            top_users = db.session.query(Issue.user_id, func.count(Issue.transaction_id).label('books_read')).group_by(Issue.user_id).order_by(desc('books_read')).limit(15)
            user_ids = [user[0] for user in top_users]
            books_read = [user[1] for user in top_users]
            user_names = [User.query.get(user_id).user_name for user_id in user_ids]
            data = [{'user_name': user_name, 'books_read': books_read} for user_name, books_read in zip(user_names, books_read)]

        if data:
            return data, 200
        else:
            return jsonify({'message': 'No data available for the provided parameter'}), 404
