from flask_sqlalchemy import SQLAlchemy
from flask import Flask,Columns,relationships

db = SQLAlchemy()

class Artist(db.Model,):
    __tablename__ = "artists"
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String)
    bio = db.Column(db.String)
    artist = db.relationship("Artist", back_populates="artist")
    def __repr__(self):
        return f"<Artist {self.id} {self.name} {self.bio}"

class Artwork(db.Model):
    __tablename__ = "artworks"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String,nullable = False)
    price = db.Column(db.Integer,nullable= False)
    artist_id = db.Column(db.Integer, foreignKey("artist.id"))

    artist = db.relationship("Artwork", back_populates = "artwork")
    def __repr__(self):
        return f"<Artwork {self.id} {self.title} {self.price}"
    