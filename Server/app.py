from flask import Flask
from models import db
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///art.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route("/")
def home():
    return "Welcome to the Art Gallery Marketplace!"

if __name__ == "__main__":
    app.run(debug=True, port=5555)