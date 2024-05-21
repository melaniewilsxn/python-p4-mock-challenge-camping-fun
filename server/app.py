#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class CampersIndex(Resource):
    def get(self):
        campers = [camper.to_dict(only=('id', 'name', 'age')) for camper in Camper.query.all()]
        return campers, 200
    
    def post(self):
        try: 
            request_json = request.get_json()
            
            name = request_json.get('name')
            age = request_json.get('age')

            new_camper = Camper(
                name=name,
                age=age
            )

            db.session.add(new_camper)
            db.session.commit()
            
            return new_camper.to_dict(only=("id", "name", "age")), 201
        except: 
            return { "errors": "400: Validation error"}, 400

class CampersByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            return camper.to_dict(), 200
        return {"error": "Camper not found"}, 404
    
    def patch(self, id):
        try:
            data = request.get_json()

            camper = Camper.query.filter_by(id=id).first()

            for attr in data:
                setattr(camper, attr, data[attr])
            
            db.session.add(camper)
            db.session.commit()

            return camper.to_dict(), 202
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            return {"error": "Camper not found"}, 404

class ActivitiesIndex(Resource):
    def get(self):
        activities = [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in Activity.query.all()]
        return activities, 200

class ActivitiesByID(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        
        if activity:
            db.session.delete(activity)
            db.session.commit()

            return {}, 204
        else:
            return {"error": "Activity not found"}, 404

class SignupIndex(Resource):
    def post(self):
        try:
            request_json = request.get_json()

            camper_id = request_json.get('camper_id')
            activity_id = request_json.get('activity_id')
            time = request_json.get('time')

            signup = Signup(
                camper_id=camper_id,
                activity_id=activity_id,
                time=time
            )

            db.session.add(signup)
            db.session.commit()

            return signup.to_dict(), 200
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400
    
api.add_resource(CampersIndex, '/campers', endpoint='campers')
api.add_resource(CampersByID, '/campers/<int:id>', endpoint='campers_by_id')
api.add_resource(ActivitiesIndex, '/activities', endpoint='activities')
api.add_resource(ActivitiesByID, '/activities/<int:id>', endpoint='activities_by_id')
api.add_resource(SignupIndex, '/signups', endpoint='signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
