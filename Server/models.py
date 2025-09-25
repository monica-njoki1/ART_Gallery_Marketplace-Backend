from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()


class Artist(db.Model, SerializerMixin):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    profile_pic = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)

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

    image_url = db.Column(db.String, nullable=True)

    # Relationships
    artist = db.relationship("Artist", back_populates="artworks", lazy="joined")
    purchases = db.relationship(
        "Purchase",
        back_populates="artwork",
        cascade="all, delete-orphan",
        lazy="select"
    )
    sells = db.relationship(
        "Sell",
        back_populates="artwork",
        cascade="all, delete-orphan",
        lazy="select"
    )

    serialize_rules = ("-artist.artworks", "-purchases.artwork", "-sells.artwork")

    def __repr__(self):
        return f"<Artwork {self.id} {self.title} ${self.price}>"


class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    
    purchases = db.relationship(
        "Purchase",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    sells = db.relationship(
        "Sell",
        back_populates="seller",
        cascade="all, delete-orphan",
        lazy="select"
    )
    cart_items = db.relationship("Cart", back_populates="user", cascade="all, delete-orphan", lazy="select")


    serialize_rules = ("-purchases.user", "-sells.seller", "-cart_items.user")

    def __repr__(self):
        return f"<User {self.id} {self.userName}>"


class Purchase(db.Model, SerializerMixin):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)
    price_paid = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="purchases", lazy="joined")
    artwork = db.relationship("Artwork", back_populates="purchases", lazy="joined")

    serialize_rules = ("-user.purchases", "-artwork.purchases")

    def __repr__(self):
        return f"<Purchase {self.id} User:{self.user_id} Artwork:{self.artwork_id} ${self.price_paid}>"


class Sell(db.Model, SerializerMixin):
    __tablename__ = "sells"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default="listed")  # listed, sold, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)

    seller = db.relationship("User", back_populates="sells", lazy="joined")
    artwork = db.relationship("Artwork", back_populates="sells", lazy="joined")

    serialize_rules = ("-seller.sells", "-artwork.sells")

    def __repr__(self):
        return f"<Sell {self.id} Artwork:{self.artwork_id} by User:{self.seller_id} ${self.price} {self.status}>"


class Cart(db.Model, SerializerMixin):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artworks.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="cart_items" lazy="joined")
    artwork = db.relationship("Artwork", back_populates="cart" lazy="joined")

    serialize_rules = ("-user.purchases", "-artwork.purchases")

    def __repr__(self):
        return f"<Cart {self.id} User:{self.user_id} Artwork:{self.artwork_id}>"
