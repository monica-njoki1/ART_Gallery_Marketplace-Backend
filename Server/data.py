from app import app, db
from models import Artist, Artwork, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Reset DB
    db.drop_all()
    db.create_all()

    
    artists = [
        Artist(name="Leonardo da Vinci", bio="Renaissance polymath, painter of the Mona Lisa."),
        Artist(name="Vincent van Gogh", bio="Post-Impressionist painter famous for Starry Night."),
        Artist(name="Frida Kahlo", bio="Mexican painter known for her self-portraits."),
        Artist(name="Claude Monet", bio="Founder of French Impressionism."),
        Artist(name="Pablo Picasso", bio="Spanish painter and sculptor, co-founder of Cubism."),
        Artist(name="Salvador Dalí", bio="Spanish surrealist painter."),
        Artist(name="Georgia O’Keeffe", bio="American modernist painter."),
        Artist(name="Rembrandt van Rijn", bio="Dutch Golden Age painter."),
        Artist(name="Edvard Munch", bio="Norwegian painter, created The Scream."),
        Artist(name="Johannes Vermeer", bio="Dutch Baroque painter, Girl with a Pearl Earring."),
    ]
    db.session.add_all(artists)
    db.session.commit()

   
    artworks = [
        Artwork(title="Mona Lisa", price=5000000, artist_id=artists[0].id,
                image_url="https://upload.wikimedia.org/wikipedia/commons/6/6a/Mona_Lisa.jpg"),
        Artwork(title="Starry Night", price=3000000, artist_id=artists[1].id,
                image_url="https://upload.wikimedia.org/wikipedia/commons/e/eb/The_Starry_Night.jpg"),
        Artwork(title="The Two Fridas", price=1500000, artist_id=artists[2].id,
                image_url="https://upload.wikimedia.org/wikipedia/en/0/0f/The_Two_Fridas.jpg"),
        Artwork(title="Water Lilies", price=2000000, artist_id=artists[3].id,
                image_url="https://upload.wikimedia.org/wikipedia/commons/0/0f/Claude_Monet_-_Water_Lilies_-_Google_Art_Project.jpg"),
        Artwork(title="Guernica", price=4000000, artist_id=artists[4].id,
                image_url="https://upload.wikimedia.org/wikipedia/en/7/74/PicassoGuernica.jpg"),
        Artwork(title="The Persistence of Memory", price=3500000, artist_id=artists[5].id,
                image_url="https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg"),
        Artwork(title="Jimson Weed", price=1200000, artist_id=artists[6].id,
                image_url="https://upload.wikimedia.org/wikipedia/en/0/00/Georgia_O%27Keeffe_-_Jimson_Weed.jpg"),
        Artwork(title="The Night Watch", price=4500000, artist_id=artists[7].id,
                image_url="https://upload.wikimedia.org/wikipedia/commons/2/20/The_Nightwatch_by_Rembrandt.jpg"),
        Artwork(title="The Scream", price=2500000, artist_id=artists[8].id,
                image_url="https://upload.wikimedia.org/wikipedia/commons/f/f4/The_Scream.jpg"),
        Artwork(title="Girl with a Pearl Earring", price=2700000, artist_id=artists[9].id,
                image_url="https://upload.wikimedia.org/wikipedia/commons/d/d7/Meisje_met_de_parel.jpg"),
    ]
    db.session.add_all(artworks)
    db.session.commit()

    
    users = [
        User(userName="alice", email="alice@example.com", password=generate_password_hash("password123")),
        User(userName="bob", email="bob@example.com", password=generate_password_hash("password123")),
        User(userName="charlie", email="charlie@example.com", password=generate_password_hash("password123")),
        User(userName="david", email="david@example.com", password=generate_password_hash("password123")),
        User(userName="eve", email="eve@example.com", password=generate_password_hash("password123")),
        User(userName="frank", email="frank@example.com", password=generate_password_hash("password123")),
        User(userName="grace", email="grace@example.com", password=generate_password_hash("password123")),
        User(userName="heidi", email="heidi@example.com", password=generate_password_hash("password123")),
        User(userName="ivan", email="ivan@example.com", password=generate_password_hash("password123")),
        User(userName="judy", email="judy@example.com", password=generate_password_hash("password123")),
    ]
    db.session.add_all(users)
    db.session.commit()

    print(" Database seeded with  artists, artworks, users!")
