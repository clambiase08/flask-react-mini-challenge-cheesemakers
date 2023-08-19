from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()


class Producer(db.Model, SerializerMixin):
    __tablename__ = "producers"
    serialize_rules = ("-cheeses.producer",)

    id = db.Column(db.Integer, primary_key=True)
    founding_year = db.Column(db.Integer)
    name = db.Column(db.String, nullable=False)
    region = db.Column(db.String)
    operation_size = db.Column(db.String)
    image = db.Column(db.String)

    cheeses = db.relationship("Cheese", backref="producer", cascade="delete")

    @validates("founding_year")
    def validate_year(self, key, year):
        if not year >= 1900:
            raise ValueError("Founding year must be after 1900")
        return year

    @validates("operation_size")
    def validate_size(self, key, operation_size):
        size = ["small", "medium", "large", "family", "corporate"]
        if operation_size not in size:
            raise ValueError("Invalid operation size")
        return operation_size

    def __repr__(self):
        return f"<Producer {self.id}>"


class Cheese(db.Model, SerializerMixin):
    __tablename__ = "cheeses"
    serialize_rules = ("-producer.cheeses",)

    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String)
    is_raw_milk = db.Column(db.Boolean)
    production_date = db.Column(db.DateTime)
    image = db.Column(db.String)
    price = db.Column(db.Float)
    producer_id = db.Column(db.Integer, db.ForeignKey("producers.id"))

    @validates("production_date")
    def validate_date(self, key, date):
        production_date = datetime.strptime(date, "%Y-%m-%d")
        if production_date >= datetime.now():
            raise ValueError("Production date must be in the past")
        return production_date

    @validates("price")
    def validate_price(self, key, price):
        if not 1.00 < price < 45.00:
            raise ValueError("Price must be between $1.00 and $45.00")
        return price

    def __repr__(self):
        return f"<Cheese {self.id}>"
