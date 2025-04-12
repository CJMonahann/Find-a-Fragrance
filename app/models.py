from app import db
from sqlalchemy import ForeignKey

#These define the DB schema
class Brands(db.Model):
    __tablename__ = 'Brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False)

    fragrances = db.relationship("Fragrances", back_populates="brand", cascade="all, delete")

class Fragrances(db.Model):
    __tablename__ = 'Fragrances'
    id = db.Column(db.Integer, primary_key=True)
    b_id = db.Column(db.Integer, ForeignKey("Brands.id", ondelete="CASCADE"))
    api_id_1 = db.Column(db.String(50), unique=False) #ID provided by API for a frag
    api_id_2 = db.Column(db.String(50), unique=False)  #ID provided by API for a frag
    perfume = db.Column(db.String(150), unique=False)
    desc = db.Column(db.String(300), unique=False)
    rating = db.Column(db.Integer, unique=False)
    img = db.Column(db.String(250), unique=False)
    url = db.Column(db.String(250), unique=False)

    brand = db.relationship("Brands", back_populates="fragrances")
    accords = db.relationship("Accords", backref="fragrance", cascade="all, delete")
    notes = db.relationship("Notes", backref="fragrance", cascade="all, delete")

class Accords(db.Model):
    __tablename__ = 'Accords'
    id = db.Column(db.Integer, primary_key=True)
    f_id = db.Column(db.Integer, ForeignKey("Fragrances.id", ondelete="CASCADE"))
    acc = db.Column(db.String(30), unique=False)

class Notes(db.Model):
    __tablename__ = 'Notes'
    id = db.Column(db.Integer, primary_key=True)
    f_id = db.Column(db.Integer, ForeignKey("Fragrances.id", ondelete="CASCADE"))
    nt = db.Column(db.String(30), unique=False)