# app.py
from flask import Flask, request, jsonify, make_response, session
from models import db, Artist, Artwork, User, Purchase, Sell, Cart
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///art.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")
# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
    profile_pic = data.get("profile_pic", "")
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
    if "profile_pic" in data:
        artist.profile_pic = data["profile_pic"]
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
    image_url = data.get("image_url")

    if not title or price is None or artist_id is None:
        return make_response(jsonify({"error": "Missing required fields: title, price, artist_id"}), 400)

    artist = Artist.query.get(artist_id)
    if not artist:
        return make_response(jsonify({"error": "Artist (artist_id) not found"}), 404)

    art = Artwork(title=title, price=price, artist_id=artist_id, image_url=image_url)
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
    if "image_url" in data:
        art.image_url = data["image_url"]
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

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    user_list = [user.to_dict(rules=("-purchases", "-password")) for user in users]
    return make_response(jsonify(user_list), 200)

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

## PURCHASES ROUTES ###
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

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"error": "No file part"}, 400
    
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    
    # store just the relative path in DB
    file_url = f"/static/uploads/{filename}"
    return {"image_url": file_url}


#### CART ROUTES ###
@app.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    artwork_id = data.get("artwork_id")

    if not user_id or not artwork_id:
        return jsonify({"error": "Missing user_id or artwork_id"}), 400

    user = User.query.get(user_id)
    art = Artwork.query.get(artwork_id)
    if not user or not art:
        return jsonify({"error": "User or Artwork not found"}), 404
    # Prevent duplicates
    existing = Cart.query.filter_by(user_id=user_id, artwork_id=artwork_id).first()
    if existing:
        return jsonify({"message": "Item already in cart", "cart_item": existing.serialize()}), 200

    item = Cart(user_id=user_id, artwork_id=artwork_id)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.serialize()), 201

@app.route("/cart/<int:user_id>", methods=["GET"])
def view_cart(user_id):
    user = User.query.get_or_404(user_id)
    items = Cart.query.filter_by(user_id=user.id).all()
    return jsonify([it.serialize() for it in items]), 200

@app.route("/cart/<int:cart_id>", methods=["DELETE"])
def remove_cart_item(cart_id):
    item = Cart.query.get_or_404(cart_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Cart item removed"}), 200

@app.route("/cart/checkout/<int:user_id>", methods=["POST"])
def checkout_cart(user_id):
    user = User.query.get_or_404(user_id)
    items = Cart.query.filter_by(user_id=user.id).all()
    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    purchases = []
    for it in items:
        art = it.artwork
        purchase = Purchase(
            user_id=user.id,
            artwork_id=art.id,
            price_paid=art.price,
            date=datetime.utcnow()
        )
        db.session.add(purchase)
        purchases.append(purchase)
        db.session.delete(it)  # clear cart

    db.session.commit()
    return jsonify({"message": "Checkout complete", "purchases": [p.serialize() for p in purchases]}), 201


@app.route("/seed-check", methods=["GET"])
def seed_check():
    counts = {
        "artists": Artist.query.count(),
        "artworks": Artwork.query.count(),
        "users": User.query.count(),
        "purchases": Purchase.query.count(),
        "cart": Cart.query.count()
    }
    return jsonify(counts), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5555)
