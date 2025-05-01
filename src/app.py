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
from models import db, User, Planet, Favorite , People
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
#---------------------------------USER---------------------------------------
@app.route('/users', methods=['GET'])
def get_all_user():

    users= User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user= User.query.get_or_404(user_id)
    return jsonify(user.serialize())

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


@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_all_favorites(user_id):
    user= User.query.get(user_id)
    if not user:
        return jsonify({"error": "No se ha encontrado el usuario"})
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify({"FAVORITES":[fav.serialize() for fav in favorites]}), 200



#---------------------------------PLANETS---------------------------------------

@app.route("/planets", methods=['GET'])
def get_all_planets():
    planets= Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route("/planets/<int:planet_id>",methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"eror": "Planeta no encontrado"})
    return jsonify(planet.serialize()), 200



@app.route('/planet',methods=['POST'])
def create_planet():
    data= request.get_json()
    name=data.get("name")
    picture_url=data.get("picture_url")

    if not name:
        return jsonify({"error":"El nombre es obligatorio"})
    planet= Planet(name=name,picture_url=picture_url)
    db.session.add(planet)
    db.session.commit()
    db.session.commit()
    return jsonify({"message": "Planet created"}), 201

@app.route('/planet/<int:planet_id>',methods=['PUT'])
def modify_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}),404
    data= request.get_json()
    if 'name' in data:
        planet.name= data['name']
    if 'picture_url' in data:
        planet.picture_url= data['picture_url']
    db.session.commit()

    return jsonify({"message": "Planeta modificado"})

@app.route('/planet/<int:planet_id>',methods=['DELETE'])
def delete_planet(planet_id):
    planet=Planet.query.filter_by(id=planet_id).first()

    if not planet:
        return jsonify({"error": "Planeta no encontrado"}),404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planeta eliminado"}), 201

@app.route('/user/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404

    existing_fav = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_fav:
        return jsonify({"message": "Ya es favorito"}), 200

    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"message": "Planeta agregado a favoritos"}), 201


@app.route('/user/<int:user_id>/favorite/planet/<int:planet_id>',methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    favorite= Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "No encontrado"}),404
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Eliminado correctamente"}),200

#---------------------------------PEOPLE---------------------------------------

@app.route('/people', methods=['GET'])
def get_people():
    persons = People.query.all()
    return jsonify([person.serialize() for person in persons])

@app.route("/people/<int:people_id>",methods=['GET'])
def get_people_id(people_id):
    planet = People.query.get_or_404(people_id)
    return jsonify(planet.serialize()), 200

@app.route('/people', methods=['POST'])
def add_person():
    data= request.get_json()
    name=data.get('name')
    mass= data.get('mass')

    if not name:
        return jsonify({"error": "Obligatorio el nombre"})
    addPerson = People(name=name, mass = mass )
    db.session.add(addPerson)
    db.session.commit()
    return jsonify({"message": "Personaje creado"})

@app.route('/people/<int:people_id>', methods=['PUT'])
def modify_people(people_id):
    person= People.query.get(people_id)
    if not person:
        return jsonify({"error" : "Personaje no encontrado" })
    
    data =request.get_json()
    if 'name' in data:
        person.name= data['name']
    if 'mass' in data:
        person.mass= data['mass']
    db.session.commit()

    return jsonify({"message" : "Personaje modificado"})

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_people(people_id):
    people= People.query.filter_by(id=people_id).first()

    if not people:
        return jsonify({"error" :  "Personaje no encontrad0"}),404
    
    db.session.delete(people)
    db.session.commit()

    return jsonify({"message": " Eliminado correctamente"})

@app.route("/user/<int:user_id>/favorite/people/<int:people_id>", methods=['POST'])
def add_favorite_people(user_id, people_id):
    user= User.query.get(user_id)
    person = People.query.get(people_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if not person:
        return jsonify({"error": "Personaje no encontrado"}), 404
    
    existing_fav = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()

    if existing_fav:
        return jsonify({"message": "ya esta en favorito"})
    favorite = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Personaje añadido a favoritos"})



@app.route('/user/<int:user_id>/favorite/people/<int:people_id>',methods=['DELETE'])
def delete_favorite_people(user_id, people_id):
    favorite= Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"error": "No encontrado"}),404
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Eliminado correctamente"}),200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
