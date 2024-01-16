import sys
import os

# Add the parent directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Now you can import create_app and other modules from the app package
from app import create_app, db

from app.models import Power, Hero, HeroPower

app = create_app()

# Rest of your seeding script...

# Seeding heroes
print("🦸‍♀️ Seeding heroes...")
heroes_data = [
    {"name": "Kamala Khan", "super_name": "Ms. Marvel"},
    # Rest of your hero data...
]

with app.app_context():
    for hero_info in heroes_data:
        hero = Hero(**hero_info)
        db.session.add(hero)

    db.session.commit()

# Seeding powers
print("🦸‍♀️ Seeding powers...")
powers_data = [
    {"name": "super strength", "description": "gives the wielder super-human strengths"},
    {"name": "flight", "description": "gives the wielder the ability to fly through the skies at supersonic speed"},
    {"name": "super human senses", "description": "allows the wielder to use her senses at a super-human level"},
    {"name": "elasticity", "description": "can stretch the human body to extreme lengths"}
]

with app.app_context():
    for power_info in powers_data:
        power = Power(**power_info)
        db.session.add(power)

    db.session.commit()

# Adding powers to heroes
print("🦸‍♀️ Adding powers to heroes...")
strengths = ["Strong", "Weak", "Average"]
heroes = Hero.query.all()

with app.app_context():
    for hero in heroes:
        for _ in range(randint(1, 3)):
            # get a random power
            power = Power.query.order_by(func.random()).first()

            hero_power = HeroPower(hero_id=hero.id, power_id=power.id, strength=choice(strengths))
            db.session.add(hero_power)

    db.session.commit()

print("🦸‍♀️ Done seeding!")
