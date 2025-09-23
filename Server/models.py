# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin  # using the installed library

db = SQLAlchemy()


class Artist(db.Model, SerializerMixin):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)

    # One-to-many: an artist has many artworks
    artworks = db.relationship(
        "Artwork",
        back_populates="artist",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Artist {self.id} {self.name}>"


class Artwork(db.Model, SerializerMixin):
    __tablename__ = "artworks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)

    # Many-to-one: an artwork belongs to one artist
    artist = db.relationship("Artist", back_populates="artworks", lazy="joined")

    def __repr__(self):
        return f"<Artwork {self.id} {self.title} ${self.price}>"
