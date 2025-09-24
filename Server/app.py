# app.py
from flask import Flask, request, jsonify, make_response, session
from models import db, Artist, Artwork, User, Purchase
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///art.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def home():
    return "Welcome to the Art Gallery Marketplace!"


### ARTISTS ROUTES ###
@app.route("/artists", methods=["GET"])
def get_artists():
    artists = Artist.query.all()
    artist_list = [artist.to_dict(rules=("-artworks.artist",)) for artist in artists]
    return make_response(jsonify(artist_list), 200)


@app.route("/artists/<int:artist_id>", methods=["GET"])
def get_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return make_response(jsonify({"error": "Artist not found"}), 404)

    # include artworks but prevent recursion back to artist
    return make_response(jsonify(artist.to_dict(rules=("-artworks.artist",))), 200)


@app.route("/artists", methods=["POST"])
def create_artist():
    data = request.get_json() or {}
    name = data.get("name")
    bio = data.get("bio", "")

    if not name:
        return make_response(jsonify({"error": "Missing 'name' field"}), 400)

    artist = Artist(name=name, bio=bio)
    db.session.add(artist)
    db.session.commit()
    return make_response(jsonify(artist.to_dict(rules=("-artworks",))), 201)


@app.route("/artists/<int:artist_id>", methods=["PATCH"])
def update_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return make_response(jsonify({"error": "Artist not found"}), 404)

    data = request.get_json() or {}
    if "name" in data:
        artist.name = data["name"]
    if "bio" in data:
        artist.bio = data["bio"]

    db.session.commit()
    return make_response(jsonify(artist.to_dict(rules=("-artworks",))), 200)


@app.route("/artists/<int:artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return make_response(jsonify({"error": "Artist not found"}), 404)

    db.session.delete(artist)
    db.session.commit()
    return make_response(jsonify({"message": "Artist successfully deleted"}), 200)


### ARTWORKS ROUTES ###
@app.route("/artworks", methods=["GET"])
def get_artworks():
    artworks = Artwork.query.all()
    artwork_list = [art.to_dict(rules=("-artist.artworks",)) for art in artworks]
    return make_response(jsonify(artwork_list), 200)


@app.route("/artworks/<int:artwork_id>", methods=["GET"])
def get_artwork(artwork_id):
    art = Artwork.query.get(artwork_id)
    if not art:
        return make_response(jsonify({"error": "Artwork not found"}), 404)

    # include artist but not their artworks
    return make_response(jsonify(art.to_dict(rules=("-artist.artworks",))), 200)


@app.route("/artworks", methods=["POST"])
def create_artwork():
    data = request.get_json() or {}
    title = data.get("title")
    price = data.get("price")
    artist_id = data.get("artist_id")

    if not title or price is None or artist_id is None:
        return make_response(jsonify({"error": "Missing required fields: title, price, artist_id"}), 400)

    artist = Artist.query.get(artist_id)
    if not artist:
        return make_response(jsonify({"error": "Artist (artist_id) not found"}), 404)

    art = Artwork(title=title, price=price, artist_id=artist_id)
    db.session.add(art)
    db.session.commit()
    return make_response(jsonify(art.to_dict(rules=("-artist.artworks",))), 201)


@app.route("/artworks/<int:artwork_id>", methods=["PATCH"])
def update_artwork(artwork_id):
    art = Artwork.query.get(artwork_id)
    if not art:
        return make_response(jsonify({"error": "Artwork not found"}), 404)

    data = request.get_json() or {}
    if "title" in data:
        art.title = data["title"]
    if "price" in data:
        art.price = data["price"]
    if "artist_id" in data:
        new_artist = Artist.query.get(data["artist_id"])
        if not new_artist:
            return make_response(jsonify({"error": "New artist_id not found"}), 404)
        art.artist_id = data["artist_id"]

    db.session.commit()
    return make_response(jsonify(art.to_dict(rules=("-artist.artworks",))), 200)


@app.route("/artworks/<int:artwork_id>", methods=["DELETE"])
def delete_artwork(artwork_id):
    art = Artwork.query.get(artwork_id)
    if not art:
        return make_response(jsonify({"error": "Artwork not found"}), 404)

    db.session.delete(art)
    db.session.commit()
    return make_response(jsonify({"message": "Artwork successfully deleted"}), 200)


### USERS ROUTES ###
@app.route("/signup", methods=["POST"])
def signup_user():
    data = request.get_json() or {}
    if not data.get("userName") or not data.get("email") or not data.get("password"):
        return make_response(jsonify({"error": "Missing required fields: userName, email, password"}), 400)

        #hash password
    hashed_password = generate_password_hash(data["password"])

    user = User(userName=data["userName"], email=data["email"], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return make_response(jsonify(user.to_dict(rules=("-purchases", "-password"))), 201)


@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}
    if not data.get("email") or not data.get("password"):
        return make_response(jsonify({"error": "Missing required fields: email, password"}), 400)

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return make_response(jsonify({"error": "Invalid email or password"}), 401)
    
    session['user_id'] = user.id  
    return make_response(jsonify({"message": f"welcome back, {user.userName}!"}), 200)


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop('user_id', None)
    return make_response(jsonify({"message": "User logged out successfully"}), 200)


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)

    return make_response(jsonify(user.to_dict(rules=("-purchases.user",))), 200)

@app.route("/users/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)

    data = request.get_json() or {}
    if "userName" in data:
        user.userName = data["userName"]
    if "email" in data:
        user.email = data["email"]

    db.session.commit()
    return make_response(jsonify(user.to_dict(rules=("-purchases",))), 200)

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)

    db.session.delete(user)
    db.session.commit()
    return make_response(jsonify({"message": "User successfully deleted"}), 200)

### PURCHASES ROUTES ###
@app.route("/purchases", methods=["POST"])
def create_purchase():
    if not session.get('user_id'):
        return make_response(jsonify({"error": "Authentication required"}), 401)
    data = request.get_json() or {}
    user_id = data.get("user_id")
    artwork_id = data.get("artwork_id")
    price_paid = data.get("price_paid")
    date = data.get("date")

    if not user_id or not artwork_id or price_paid is None or not date:
        return make_response(jsonify({"error": "Missing required fields: user_id, artwork_id, price_paid, date"}), 400)

    user = User.query.get(user_id)
    if not user:
        return make_response(jsonify({"error": "User (user_id) not found"}), 404)

    artwork = Artwork.query.get(artwork_id)
    if not artwork:
        return make_response(jsonify({"error": "Artwork (artwork_id) not found"}), 404)

    purchase = Purchase(user_id=user_id, artwork_id=artwork_id, price_paid=price_paid, date=date)
    db.session.add(purchase)
    db.session.commit()
    return make_response(jsonify(purchase.to_dict(rules=("-user.purchases", "-artwork.purchases"))), 201)


@app.route("/purchases/<int:purchase_id>", methods=["GET"])
def get_purchase(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    if not purchase:
        return make_response(jsonify({"error": "Purchase not found"}), 404)

    return make_response(jsonify(purchase.to_dict(rules=("-user.purchases", "-artwork.purchases"))), 200)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5555)
