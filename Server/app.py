from flask import Flask, request, jsonify, make_response, session
from models import db, Artist, Artwork, User, Purchase, Sell, Cart
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app,supports_credentials=True)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///art.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

db.init_app(app)
migrate = Migrate(app, db)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def home():
    return "Welcome to the Art Gallery Marketplace!"

# --- ARTISTS ---
@app.route("/artists", methods=["GET"])
def get_artists():
    artists = Artist.query.all()
    return jsonify([a.to_dict(rules=("-artworks.artist",)) for a in artists])

@app.route("/artists/<int:artist_id>", methods=["GET"])
def get_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    return jsonify(artist.to_dict(rules=("-artworks.artist",)))

@app.route("/artists", methods=["POST"])
def create_artist():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "Missing 'name'"}), 400
    artist = Artist(name=data["name"], bio=data.get("bio"), profile_pic=data.get("profile_pic"))
    db.session.add(artist)
    db.session.commit()
    return jsonify(artist.to_dict(rules=("-artworks",))), 201

@app.route("/artists/<int:artist_id>", methods=["PATCH"])
def update_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    data = request.get_json() or {}
    if "name" in data: artist.name = data["name"]
    if "bio" in data: artist.bio = data["bio"]
    if "profile_pic" in data: artist.profile_pic = data["profile_pic"]
    db.session.commit()
    return jsonify(artist.to_dict(rules=("-artworks",)))

@app.route("/artists/<int:artist_id>", methods=["DELETE"])
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    db.session.delete(artist)
    db.session.commit()
    return jsonify({"message": "Artist deleted"}), 200

# --- ARTWORKS ---
@app.route("/artworks", methods=["GET"])
def get_artworks():
    arts = Artwork.query.all()
    return jsonify([a.to_dict(rules=("-artist.artworks",)) for a in arts])

@app.route("/artworks/<int:artwork_id>", methods=["GET"])
def get_artwork(artwork_id):
    art = Artwork.query.get_or_404(artwork_id)
    return jsonify(art.to_dict(rules=("-artist.artworks",)))

@app.route("/artworks", methods=["POST"])
def create_artwork():
    data = request.get_json() or {}
    if not data.get("title") or data.get("price") is None or data.get("artist_id") is None:
        return jsonify({"error": "Missing required fields"}), 400
    artist = Artist.query.get(data["artist_id"])
    if not artist: return jsonify({"error": "Artist not found"}), 404
    art = Artwork(
        title=data["title"],
        price=data["price"],
        artist_id=data["artist_id"],
        image_url=data.get("image_url"),
        description=data.get("description")
    )
    db.session.add(art)
    db.session.commit()
    return jsonify(art.to_dict(rules=("-artist.artworks",))), 201

@app.route("/artworks/<int:artwork_id>", methods=["PATCH"])
def update_artwork(artwork_id):
    art = Artwork.query.get_or_404(artwork_id)
    data = request.get_json() or {}
    if "title" in data: art.title = data["title"]
    if "price" in data: art.price = data["price"]
    if "image_url" in data: art.image_url = data["image_url"]
    if "description" in data: art.description = data["description"]
    if "artist_id" in data:
        new_artist = Artist.query.get(data["artist_id"])
        if not new_artist: return jsonify({"error": "Artist not found"}), 404
        art.artist_id = data["artist_id"]
    db.session.commit()
    return jsonify(art.to_dict(rules=("-artist.artworks",)))

@app.route("/artworks/<int:artwork_id>", methods=["DELETE"])
def delete_artwork(artwork_id):
    art = Artwork.query.get_or_404(artwork_id)
    db.session.delete(art)
    db.session.commit()
    return jsonify({"message": "Artwork deleted"}), 200

# --- USERS ---
# --- USERS ---
@app.route("/signup", methods=["POST"])
def signup_user():
    data = request.get_json() or {}
    if not data.get("userName") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(data["password"])
    user = User(
        userName=data["userName"],
        email=data["email"],
        password=hashed_password,
        role=data.get("role", "user")  # NEW
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict(rules=("-purchases", "-sells", "-cart_items", "-password"))), 201


@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not check_password_hash(user.password, data.get("password", "")):
        return jsonify({"error": "Invalid credentials"}), 401

    session['user_id'] = user.id
    return jsonify({
        "message": f"Welcome back, {user.userName}!",
        "user": user.to_dict(rules=("-purchases", "-sells", "-cart_items", "-password"))
    })


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out"})

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict(rules=("-purchases", "-password")) for u in users])

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict(rules=("-purchases.user",)))

@app.route("/users/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    if "userName" in data: user.userName = data["userName"]
    if "email" in data: user.email = data["email"]
    db.session.commit()
    return jsonify(user.to_dict(rules=("-purchases",)))

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

# --- PURCHASES ---
@app.route("/purchases", methods=["POST"])
def create_purchase():
    if not session.get('user_id'):
        return jsonify({"error": "Authentication required"}), 401
    data = request.get_json() or {}
    user_id = data.get("user_id")
    artwork_id = data.get("artwork_id")
    price_paid = data.get("price_paid")
    date = data.get("date")
    if not user_id or not artwork_id or price_paid is None or not date:
        return jsonify({"error": "Missing fields"}), 400
    user = User.query.get(user_id)
    artwork = Artwork.query.get(artwork_id)
    if not user or not artwork:
        return jsonify({"error": "User or Artwork not found"}), 404
    purchase = Purchase(user_id=user_id, artwork_id=artwork_id, price_paid=price_paid, date=date)
    db.session.add(purchase)
    db.session.commit()
    return jsonify(purchase.to_dict(rules=("-user.purchases", "-artwork.purchases"))), 201

@app.route("/purchases/<int:purchase_id>", methods=["GET"])
def get_purchase(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    return jsonify(purchase.to_dict(rules=("-user.purchases", "-artwork.purchases")))

@app.route("/purchases/user/<int:user_id>", methods=["GET"])
def get_user_purchases(user_id):
    """Get all purchases for a given user"""
    purchases = Purchase.query.filter_by(user_id=user_id).all()
    return jsonify([
        p.to_dict(rules=("-user.purchases", "-artwork.purchases"))
        for p in purchases
    ]), 200

@app.route("/purchases/<int:purchase_id>", methods=["DELETE"])
def sell_artwork(purchase_id):
    """
    Simulate selling artwork:
    - Delete purchase record
    - Add entry into Sell table
    """
    purchase = Purchase.query.get_or_404(purchase_id)
    sell = Sell(
        price=purchase.price_paid,
        seller_id=purchase.user_id,
        artwork_id=purchase.artwork_id,
        status="listed"
    )
    db.session.add(sell)
    db.session.delete(purchase)
    db.session.commit()
    return jsonify({"message": "Artwork listed for sale", "sell": sell.to_dict()}), 200

# --- UPLOAD ---
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    file.save(filepath)
    return jsonify({"image_url": f"/{filepath}"}), 201

# --- CART ---
@app.route("/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    artwork_id = data.get("artwork_id")
    if not user_id or not artwork_id:
        return jsonify({"error": "Missing fields"}), 400
    user = User.query.get(user_id)
    art = Artwork.query.get(artwork_id)
    if not user or not art:
        return jsonify({"error": "User or Artwork not found"}), 404
    existing = Cart.query.filter_by(user_id=user_id, artwork_id=artwork_id).first()
    if existing:
        return jsonify({"message": "Item already in cart", "cart_item": existing.to_dict()}), 200
    item = Cart(user_id=user_id, artwork_id=artwork_id)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@app.route("/cart/<int:user_id>", methods=["GET"])
def view_cart(user_id):
    user = User.query.get_or_404(user_id)
    items = Cart.query.filter_by(user_id=user.id).all()
    return jsonify([i.to_dict() for i in items]), 200

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
        purchase = Purchase(user_id=user.id, artwork_id=art.id, price_paid=art.price, date=datetime.utcnow())
        db.session.add(purchase)
        purchases.append(purchase)
        db.session.delete(it)
    db.session.commit()
    return jsonify({"message": "Checkout complete", "purchases": [p.to_dict(rules=("-user.purchases","-artwork.purchases")) for p in purchases]}), 201

# --- SEED CHECK ---
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
    app.run(debug=True, port=5000)
