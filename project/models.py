# from flask_sqlalchemy import SQLAlchemy

from db_connection import db

class User(db.Model):
    __tablename__ = "users"  # Rename table

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    university_grade = db.Column(db.Float, nullable=False)
    extend_existing=True

