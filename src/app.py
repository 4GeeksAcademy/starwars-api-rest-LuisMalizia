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
from models import db, User, Planets, People, Favorites
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

@app.route('/user', methods=['GET'])
def get_user():
    data = db.session.scalars(db.select(User)).all()
    result = list(map(lambda item: item.serialize(),data))

    if result == []:
        return jsonify({"msg":"there are no users"}), 404

    response_body = {
        "results": result
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_all_people():
    data = db.session.scalars(db.select(People)).all()
    result = [item.serialize() for item in data]

    if not result:
        return jsonify({"msg": "No hay registros de personas"}), 404

    response_body = {
        "results": result
    }

    return jsonify(response_body), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_people(people_id):
    try:
        people = db.session.execute(db.select(People).filter_by(id=people_id)).scalar_one()
        return jsonify({"result": people.serialize()}), 200
    except:
        return jsonify({"msg": "La persona no existe"}), 404


@app.route('/planets', methods=['GET'])
def get_all_planets():
    data = db.session.scalars(db.select(Planets)).all()
    result = [item.serialize() for item in data]

    if not result:
        return jsonify({"msg": "No hay registros de planetas"}), 404

    response_body = {
        "results": result
    }

    return jsonify(response_body), 200


@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    try:
        planet = db.session.execute(db.select(Planets).filter_by(id=planets_id)).scalar_one()
        return jsonify({"result": planet.serialize()}), 200
    except:
        return jsonify({"msg": "El planeta no existe"}), 404


@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    try:
        favorites = db.session.scalars(db.select(Favorites).filter_by(user_id=user_id)).all()
        if favorites:
            return jsonify({"results": [fav.serialize() for fav in favorites]}), 200
        return jsonify({"msg": "El usuario no tiene favoritos"}), 404
    except Exception as e:
        return jsonify({"msg": "Error", "error": str(e)}), 500


@app.route('/user/<int:user_id>/favorites/planets/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    try:
        user_exists = db.session.query(db.select(User).filter_by(id=user_id).exists()).scalar()
        planet_exists = db.session.query(db.select(Planets).filter_by(id=planet_id).exists()).scalar()

        if not user_exists or not planet_exists:
            return jsonify({"msg": "Usuario o planeta no encontrado"}), 404

        favorite_exists = db.session.query(db.select(Favorites).filter_by(user_id=user_id, planets_id=planet_id).exists()).scalar()
        if favorite_exists:
            return jsonify({"msg": "El favorito ya existe"}), 400

        new_favorite = Favorites(user_id=user_id, planets_id=planet_id, people_id=None)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"msg": "Favorito añadido"}), 201
    except Exception as e:
        return jsonify({"msg": "Error", "error": str(e)}), 500


@app.route('/user/<int:user_id>/favorites/people/<int:people_id>', methods=['POST'])
def add_favorite_person(user_id, people_id):
    try:
        user_exists = db.session.query(db.select(User).filter_by(id=user_id).exists()).scalar()
        person_exists = db.session.query(db.select(People).filter_by(id=people_id).exists()).scalar()

        if not user_exists or not person_exists:
            return jsonify({"msg": "Usuario o persona no encontrado"}), 404

        favorite_exists = db.session.query(db.select(Favorites).filter_by(user_id=user_id, people_id=people_id).exists()).scalar()
        if favorite_exists:
            return jsonify({"msg": "El favorito ya existe"}), 400

        new_favorite = Favorites(user_id=user_id, people_id=people_id, planets_id=None)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"msg": "Favorito añadido"}), 201
    except Exception as e:
        return jsonify({"msg": "Error", "error": str(e)}), 500


@app.route('/user/<int:user_id>/favorites/planets/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    try:
        favorite = db.session.execute(db.select(Favorites).filter_by(user_id=user_id, planets_id=planet_id)).scalar_one_or_none()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"msg": "Favorito eliminado"}), 200
        return jsonify({"msg": "Favorito no encontrado"}), 404
    except Exception as e:
        return jsonify({"msg": "Error", "error": str(e)}), 500


@app.route('/user/<int:user_id>/favorites/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(user_id, people_id):
    try:
        favorite = db.session.execute(db.select(Favorites).filter_by(user_id=user_id, people_id=people_id)).scalar_one_or_none()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"msg": "Favorito eliminado"}), 200
        return jsonify({"msg": "Favorito no encontrado"}), 404
    except Exception as e:
        return jsonify({"msg": "Error", "error": str(e)}), 500