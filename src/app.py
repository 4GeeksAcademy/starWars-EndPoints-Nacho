"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet
from sqlalchemy.exc import IntegrityError
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_all_user():

    users= User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route("/planets", methods=['get'])
def get_all_planets():
    planets= Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/user', methods=['POST'])
def create_user():
    data=request.get_json()
    first_name=data.get("first_name")
    last_name=data.get("last_name")
    email=data.get("email")
    password=data.get("password")
    if not( first_name and last_name and email and password):
        return jsonify({"error":"Faltan campos obligados "}), 400
    user = User(first_name=first_name, last_name= last_name, email=email, password=password)
    db.session.add(user)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({"error": "El email ya esta registrado"}), 409

    return jsonify({
        "first_name":user.first_name,
        "last_name":user.last_name,
        "email":user.email,
        "id":user.id
    }) ,200


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user= User.query.get_or_404(user_id)
    return jsonify(user.serialize())


@app.route('/planet',methods=['POST'])
def create_planet():
    data= request.get_json()
    name=data.get("name")
    picture_url=data.get("picture_url")
    users_ids=data.get("users",[])

    if not name:
        return jsonify({"error":"El nombre es obligatorio"})
    planet= Planet(name=name,picture_url=picture_url)
    db.session.add(planet)
    db.session.commit()

    for user_id in users_ids:
        user= User.query.get(user_id)
        if user: 
            planet.users.append(user)
        
    db.session.commit()
    return jsonify({"message": "Planet created"}), 201
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
