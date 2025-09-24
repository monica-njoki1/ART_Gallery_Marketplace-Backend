from app import app
from models import db, Artist, Artwork, User, Purchase, Sell
from datetime import datetime

with app.app_context():
    db.drop_all()
    db.create_all()

    # Artists
    artist1 = Artist(name="Pablo Picasso", bio="Spanish painter, sculptor, printmaker, ceramicist and stage designer.")
    artist2 = Artist(name="Frida Kahlo", bio="Mexican painter known for self-portraits and works inspired by nature.")

    db.session.add_all([artist1, artist2])
    db.session.commit()

    # Artworks
    art1 = Artwork(title="Les Demoiselles d'Avignon", price=1000000, artist=artist1)
    art2 = Artwork(title="The Weeping Woman", price=800000, artist=artist1)
    art3 = Artwork(title="The Two Fridas", price=500000, artist=artist2)

    db.session.add_all([art1, art2, art3])
    db.session.commit()

    # Users
    user1 = User(userName="alice", email="alice@example.com", password="password123")
    user2 = User(userName="bob", email="bob@example.com", password="password123")

    db.session.add_all([user1, user2])
    db.session.commit()

    # Purchases
    purchase1 = Purchase(user=user1, artwork=art1, price_paid=1000000, date=datetime.utcnow())
    purchase2 = Purchase(user=user2, artwork=art3, price_paid=500000, date=datetime.utcnow())

    db.session.add_all([purchase1, purchase2])
    db.session.commit()

    # Sell listings
    sell1 = Sell(price=1200000, seller=user1, artwork=art1, status="listed")
    sell2 = Sell(price=600000, seller=user2, artwork=art3, status="listed")

    db.session.add_all([sell1, sell2])
    db.session.commit()

    print("✅ Database seeded successfully!")
