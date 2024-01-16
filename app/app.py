from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///heroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    super_name = db.Column(db.String(255), nullable=False)
    hero_powers = db.relationship('HeroPower', backref='hero', lazy=True)

class Power(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    hero_powers = db.relationship('HeroPower', backref='power', lazy=True)

class HeroPower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hero_id = db.Column(db.Integer, db.ForeignKey('hero.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('power.id'), nullable=False)
    strength = db.Column(db.String(20), nullable=False)

class PowerSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()

class HeroSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    super_name = fields.String()
    powers = fields.Nested(PowerSchema, many=True, exclude=('id',))

class HeroPowerSchema(Schema):
    id = fields.Integer()
    hero_id = fields.Integer()
    power_id = fields.Integer()
    strength = fields.String()

power_schema = PowerSchema()
powers_schema = PowerSchema(many=True)
hero_schema = HeroSchema()
heroes_schema = HeroSchema(many=True)
hero_power_schema = HeroPowerSchema()

# Create tables
with app.app_context():
    db.create_all()

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    result = heroes_schema.dump(heroes)
    return jsonify(result)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
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
def get_power(id):
    power = Power.query.get(id)
    if power:
        result = power_schema.dump(power)
        return jsonify(result)
    else:
        return jsonify({"error": "Power not found"}), 404

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
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"errors": ["IntegrityError: {}".format(str(e))]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

if __name__ == '__main__':
    app.run(port=5555)
