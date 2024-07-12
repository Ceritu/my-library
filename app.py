from flask import Flask, request, jsonify
from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import Schema, fields, ValidationError

Base = declarative_base()

class Book(Base): 
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    published_date = Column(Date)
    ISBN = Column(String)
    availability = Column(String)

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    membership_date = Column(Date)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    member_id = Column(Integer, ForeignKey('members.id'))
    borrow_date = Column(Date)
    return_date = Column(Date)

# SQLite database file named 'lib.db'
engine = create_engine('sqlite:///lib.db')
Base.metadata.create_all(engine)  # This line creates all tables in the database
Session = sessionmaker(bind=engine)

app = Flask(__name__)

class BookSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    published_date = fields.Date()
    ISBN = fields.Str()
    availability = fields.Str()

book_schema = BookSchema()

@app.route('/books', methods=['POST'])
def create_book():
    try:
        # Validate input data
        data = book_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    session = Session()
    new_book = Book(**data)
    session.add(new_book)

    try:
        session.commit()
    except SQLAlchemyError as e:
        print(str(e.__dict__['orig']))
        session.rollback()
        return jsonify({"message": "An error occurred while creating the book."}), 500

    return jsonify({"id": new_book.id}), 201

@app.route('/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_book(book_id):
    session = Session()
    book = session.query(Book).get(book_id)

    if request.method == 'GET':
        if book is None:
            return jsonify({"message": "Book not found"}), 404
        return jsonify(book_schema.dump(book)), 200

    elif request.method == 'PUT':
        if book is None:
            return jsonify({"message": "Book not found"}), 404
        try:
            data = book_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400
        for key, value in data.items():
            setattr(book, key, value)
        session.commit()
        return jsonify(book_schema.dump(book)), 200

    elif request.method == 'DELETE':
        if book is None:
            return jsonify({"message": "Book not found"}), 404
        session.delete(book)
        session.commit()
        return jsonify({"message": "Book deleted"}), 200

class MemberSchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    membership_date = fields.Date()

member_schema = MemberSchema()

@app.route('/members', methods=['POST'])
def create_member():
    try:
        data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    session = Session()
    new_member = Member(**data)
    session.add(new_member)

    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        return jsonify({"message": "An error occurred while creating the member."}), 500

    return jsonify({"id": new_member.id}), 201

@app.route('/members/<int:member_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_member(member_id):
    session = Session()
    member = session.query(Member).get(member_id)

    if request.method == 'GET':
        if member is None:
            return jsonify({"message": "Member not found"}), 404
        return jsonify(member_schema.dump(member)), 200

    elif request.method == 'PUT':
        if member is None:
            return jsonify({"message": "Member not found"}), 404
        try:
            data = member_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400
        for key, value in data.items():
            setattr(member, key, value)
        session.commit()
        return jsonify(member_schema.dump(member)), 200

    elif request.method == 'DELETE':
        if member is None:
            return jsonify({"message": "Member not found"}), 404
        session.delete(member)
        session.commit()
        return jsonify({"message": "Member deleted"}), 200

class TransactionSchema(Schema):
    id = fields.Int(required=True)
    book_id = fields.Int(required=True)
    member_id = fields.Int(required=True)
    borrow_date = fields.Date()
    return_date = fields.Date()

transaction_schema = TransactionSchema()

@app.route('/transactions', methods=['POST'])
def create_transaction():
    try:
        data = transaction_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    session = Session()
    new_transaction = Transaction(**data)
    session.add(new_transaction)

    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        return jsonify({"message": "An error occurred while creating the transaction."}), 500

    return jsonify({"id": new_transaction.id}), 201

@app.route('/transactions/<int:transaction_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_transaction(transaction_id):
    session = Session()
    transaction = session.query(Transaction).get(transaction_id)

    if request.method == 'GET':
        if transaction is None:
            return jsonify({"message": "Transaction not found"}), 404
        return jsonify(transaction_schema.dump(transaction)), 200

    elif request.method == 'PUT':
        if transaction is None:
            return jsonify({"message": "Transaction not found"}), 404
        try:
            data = transaction_schema.load(request.json)
        except ValidationError as e:
            return jsonify(e.messages), 400
        for key, value in data.items():
            setattr(transaction, key, value)
        session.commit()
        return jsonify(transaction_schema.dump(transaction)), 200

    elif request.method == 'DELETE':
        if transaction is None:
            return jsonify({"message": "Transaction not found"}), 404
        session.delete(transaction)
        session.commit()
        return jsonify({"message": "Transaction deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
