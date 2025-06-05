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
from models import db, User, Todos
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route("/health-check", methods=["GET"])
def health_check():
    return jsonify("ok"), 200


@app.route('/user', methods=['POST'])
def add_user():
    body = request.json

    if body.get("username") is None:
        return jsonify("Se debe enviar la llave username"), 400

    if body.get("email") is None:
        return jsonify("Se debe enviar la llave email"), 400

    # User.username="", User.email=""
    user = User.query.filter_by(
        username=body["username"], email=body["email"]).first()

    if user is not None:
        user = user.serialize()

        if user.get("username") is not None or user.get("email") is not None:
            return jsonify(f"El username {body["username"]} ya se encuentra registrado")

    user = User()
    user.username = body.get("username").lower()
    user.email = body["email"]

    db.session.add(user)

    try:
        db.session.commit()
        return jsonify("Usuario registrado exitosamente"), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}"), 500


@app.route("/user", methods=["GET"])
def get_all_users():
    users = User.query.all()

    # HEcho con for
    # response_body = []
    # for item in users:
    #     response_body.append(item.serialize())

    # hecho con map
    # response_body = list(map(lambda item: item.serialize(), users))

    # List Comprehension
    # response_body = [item.serialize() for item in users]

    return jsonify([item.serialize() for item in users]), 200


@app.route("/user/<int:the_id>", methods=["GET"])
def get_one_user(the_id):
    user = User.query.get(the_id)

    if user is None:
        return jsonify("El usuario no esta registrado"), 404

    return jsonify(user.serialize())


@app.route("/todos", methods=["POST"])
def add_todo():
    # 1.- Traernos el body del request
    data = request.json
    # 2.- Validar que si sea una tarea
    if data.get("label") is None:
        return jsonify("Debes enviar la llave label"), 400
    # 3.- Creamos el molde, esta es la instancia de la clase Todos
    todo = Todos()
    # 4.- Rellenar el molde
    todo.label = data["label"]
    todo.user_id = data["user_id"]
    # 5.- Agregarla a la session de base de datos
    db.session.add(todo)
    # 6.- Agregar el commit del cambio perooooo dentro de un try except

    try:
        db.session.commit()
        return jsonify("tarea registrada exitosamente"), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}")


@app.route("/todos/<int:the_id>", methods=["PUT"])
def update_task(the_id=None):
    body = request.json

    todo = Todos.query.get(the_id)

    if body.get("is_done") is None:
        return jsonify("debes enviar una llave id_done"), 400

    if body.get("label") is None:
        return jsonify("debes enviar una llave id_done"), 400

    if todo is None:
        return jsonify("User not found"), 404

    todo.is_done = body["is_done"]
    todo.label = body["label"]

    try:
        db.session.commit()
        return jsonify(todo.serialize()), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}")


@app.route("/todos/<int:the_id>",  methods=["DELETE"])
def delete_task(the_id=None):
    todo = Todos.query.get(the_id)

    if todo is None:
        return jsonify("User not found"), 404

    db.session.delete(todo)
    try:
        db.session.commit()
        return jsonify([]), 204
    except Exception as error:
        return jsonify(f"Error: {error.args}")


@app.route("/user/<int:the_id>", methods=["DELETE"])
def delete_user(the_id=None):
    user = User.query.get(the_id)

    if user is None:
        return jsonify("User not found"), 404

    db.session.delete(user)

    try:
        db.session.commit()
        return jsonify([]), 204
    except Exception as error:
        return jsonify(f"Error: {error.args}")


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
