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

    serialize_rules = ("-artworks.artist",)

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

    # One-to-many: an artwork has many purchases
    purchases = db.relationship(
        "Purchase",
        back_populates="artwork",
        cascade="all, delete-orphan",
        lazy="select"
    )

    serialize_rules = ("-artist.artworks", "-purchases.artwork")

    def __repr__(self):
        return f"<Artwork {self.id} {self.title} ${self.price}>"


class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    # One-to-many: a user has many purchases
    purchases = db.relationship(
        "Purchase",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    

    serialize_rules = ("-purchases.user",)

    def __repr__(self):
        return f"<User {self.id} {self.userName}>"


class Purchase(db.Model, SerializerMixin):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)
    price_paid = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    # Many-to-one: a purchase belongs to one user
    user = db.relationship("User", back_populates="purchases", lazy="joined")
    # Many-to-one: a purchase belongs to one artwork
    artwork = db.relationship("Artwork", back_populates="purchases", lazy="joined")

    serialize_rules = ("-user.purchases", "-artwork.purchases")


    def __repr__(self):
        return f"<Purchase {self.id} User:{self.user_id} Artwork:{self.artwork_id} ${self.price_paid}>"


