from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_migrate import Migrate

from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///heroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
# Define your models here

class Power(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)

class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    super_name = db.Column(db.String(255), nullable=False)

class HeroPower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_id = db.Column(db.Integer, db.ForeignKey('hero.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('power.id'), nullable=False)
    strength = db.Column(db.String(20), nullable=False)

# Define your schema here

class PowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Power
    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()

class HeroSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Hero
    id = ma.auto_field()
    name = ma.auto_field()
    super_name = ma.auto_field()
    powers = ma.Nested(PowerSchema, many=True, exclude=('id',))

class HeroPowerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HeroPower
    id = ma.auto_field()
    hero_id = ma.auto_field()
    power_id = ma.auto_field()
    strength = ma.auto_field()

# Initialize your schemas

power_schema = PowerSchema()
powers_schema = PowerSchema(many=True)
hero_schema = HeroSchema()
heroes_schema = HeroSchema(many=True)
hero_power_schema = HeroPowerSchema()
hero_powers_schema = HeroPowerSchema(many=True)

# Define your routes here

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    result = heroes_schema.dump(heroes)
    return jsonify(result)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if hero:
        result = hero_schema.dump(hero)
        return jsonify(result)
    else:
        return jsonify({"error": "Hero not found"}), 404

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    result = powers_schema.dump(powers)
    return jsonify(result)

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    if power:
        result = power_schema.dump(power)
        return jsonify(result)
    else:
        return jsonify({"error": "Power not found"}), 404

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    try:
        data = request.get_json()
        power.description = data['description']
        db.session.commit()
        result = power_schema.dump(power)
        return jsonify(result)
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400

# Implement the POST /hero_powers route
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    try:
        data = request.get_json()
        hero_power = HeroPower(hero_id=data['hero_id'], power_id=data['power_id'], strength=data['strength'])
        db.session.add(hero_power)
        db.session.commit()
        hero = Hero.query.get(data['hero_id'])
        result = hero_schema.dump(hero)
        return jsonify(result)
    except (IntegrityError, ValidationError) as e:
        return jsonify({"errors": e.messages}), 400

if __name__ == '__main__':
    app.run(port=5555)
