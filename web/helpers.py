from flask import flash, render_template
from outsideapi.outsideapi import find_city, find_cities
from db import get_db

def city_add(city):
    db = get_db()
    city_id = city[5]
    existingCity = db.execute("SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid FROM cities WHERE geonameid = ?", [city_id]).fetchone()
    if existingCity:
        return 'city exists'
    db.execute('INSERT INTO cities(name, country, latitude, longitude, population, geonameid) VALUES (?, ?, ?, ?, ?, ?)', city)
    db.commit()
    flash(f"Added city - {city[0]}")

