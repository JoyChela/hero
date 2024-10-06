#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
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

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes')
def get_heroes():
    heroes = Hero.query.all()
    response = [{
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name
    } for hero in heroes]
    
    return make_response(
        jsonify(response),
        200
    )

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if hero:
        response = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "hero_powers": [{
                "hero_id": hero_power.hero_id,
                "id": hero_power.id,
                "power": {
                    "description": hero_power.power.description,
                    "id": hero_power.power.id,
                    "name": hero_power.power.name
                },
                "power_id": hero_power.power_id,
                "strength": hero_power.strength
            } for hero_power in hero.hero_powers]
        }
        return make_response(jsonify(response), 200)
    else:
        return make_response(jsonify({"error": "Hero not found"}), 404)

    

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()  
    powers_data = [
        {
            'id': power.id,  
            'name': power.name,  
            'description': power.description 
        }
        for power in powers
    ]
    return jsonify(powers_data), 200  

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id) 
    if power:
        power_data = {
            'id': power.id,  
            'name': power.name, 
            'description': power.description 
        }
        return jsonify(power_data), 200  
    else:
        return jsonify({'error': 'Power not found'}), 404  

from flask import request, jsonify

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power:
        data = request.get_json()
        if 'description' in data and data['description']:
            power.description = data['description']
            db.session.commit()
            response = {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
    else:
        return make_response(jsonify({"error": "Power not found"}), 404)


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    hero = Hero.query.get(data['hero_id'])
    power = Power.query.get(data['power_id'])
    
    if hero and power:
        new_hero_power = HeroPower(
            strength=data['strength'],
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )
        db.session.add(new_hero_power)
        db.session.commit()
        
        response = {
            "id": new_hero_power.id,
            "hero_id": new_hero_power.hero_id,
            "power_id": new_hero_power.power_id,
            "strength": new_hero_power.strength,
            "hero": {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name
            },
            "power": {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
        }
        return make_response(jsonify(response), 201)
    else:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)





if __name__ == '__main__':
    app.run(port=5555, debug=True)
