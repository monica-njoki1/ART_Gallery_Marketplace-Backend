from flask import Flask,request,make_response
from models import db,Artist,Artwork
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///art.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route("/")
def home():
    return "Welcome to the Art Gallery Marketplace!"


@app.route("/artists")
def artists():
    artists = Artist.query.all()
    artist_list = [artist.to_dict for artist in artists]
    resp = make_response(artist_list, 200)
    return resp


@app.route("/artists/<int:id>", methods=["GET","DELETE"])
def artists_by_id(id):
    artist = Artist.query.filter_by(id ==id).first()
    if not artist:
        return {"error":"Artist not found"}
    if request.method == "GET":
        return make_response(
            artist.to_dict(
                only=("id","name","bio")
            ),
            200
        )
    if request.method == "DELETE":
        db.session.delete(artist)
        db.session.commit()
        resp = make_response(
            {"message":"Artist successfully deleted"}

        )
        return resp

@app.route("/artworks")
def artworks():
    artwork = Artwork.query.all()
    artwork_list = [art.to_dict() for art in artwork]
    resp = make_response(
        artwork_list,
        200
    )
    return resp
# The route below will show the artwork details
@app.route("/artworks/")
def art_work_details():
    pass

# @app.route("")


if __name__ == "__main__":
    app.run(debug=True, port=5555)