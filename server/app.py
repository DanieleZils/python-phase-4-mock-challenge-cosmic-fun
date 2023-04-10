from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Scientist, Planet, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)


class Scientists(Resource):

    def get(self):
        scientists = Scientist.query.all()
        scientists_dict_list = [scientist.to_dict()
                                for scientist in scientists]
        response = make_response(
            scientists_dict_list,
            200
        )

        return response

    def post(self):
        data = request.get_json()
        try:
            scientist = Scientist(
                name=data['name'],
                field_of_study=data['field_of_study'],
                avatar=data['avatar']
            )

            db.session.add(scientist)
            db.session.commit()
        except Exception as e:
            return make_response({
                "errors": [e.__str__()]
            }, 422)
        response = make_response(
            scientist.to_dict(),
            201
        )
        return response


api.add_resource(Scientists, '/scientists')


class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({
                "error": "Scientist not found"
            }, 404)
        scientist_dict = scientist.to_dict(
            rules=('planets', ))
        response = make_response(scientist_dict, 200)
        return response

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        data = request.get_json()
        for attr in data:
            setattr(scientist, attr, data[attr])
        db.session.add(scientist)
        db.session.commit()

        response = make_response(scientist.to_dict(), 202)
        return response

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return make_response({
                "error": "Scientist not found"
            }, 404)

        db.session.delete(scientist)
        db.session.commit()


api.add_resource(ScientistById, '/scientists/<int:id>')


class Planets(Resource):
    def get(self):
        planets = [planet.to_dict() for planet in Planet.query.all()]
        return make_response(planets, 200)


api.add_resource(Planets, '/planets')

# def post(self):
#         data = request.get_json()
#         try:
#             scientist = Scientist(
#                 name=data['name'],
#                 field_of_study=data['field_of_study'],
#                 avatar=data['avatar']
#             )

#             db.session.add(scientist)
#             db.session.commit()
#         except Exception as e:
#             return make_response({
#                 "errors": [e.__str__()]
#             }, 422)
#         response = make_response(
#             scientist.to_dict(),
#             201
#         )
#         return response

class Missions(Resource):

    def post(self):
        data = request.get_json()
        
        try:
            mission = Mission(
                name=data['name'],
                scientist_id=data['scientist_id'],
                planet_id=data['planet_id']
            )

            db.session.add(mission)
            db.session.commit()

        except Exception as e:
            return make_response({
                'error': ['validation error']}, 422)
            
        planet = Planet.query.get(mission.planet_id)

    # # Create a response with the planet info
        response_data = {
            'id': planet.id,
            'name': planet.name,
            'distance_from_earth': planet.distance_from_earth,
            'nearest_star': planet.nearest_star,
            'image': planet.image
             }
        
        response_dict = response_data.to_dict()
        
        response = make_response(response_dict, 201)  # Update response with planet info
        
        return response

api.add_resource(Missions, '/missions')


if __name__ == '__main__':
    app.run(port=5555)
