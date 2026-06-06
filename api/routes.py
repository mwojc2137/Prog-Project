from flask import Blueprint, request, jsonify, abort
from db import get_db
from outsideapi.outsideapi import find_city_by_id, find_cities

api = Blueprint('api', __name__)

@api.route('/cities', methods=['GET']) #curl http://127.0.0.1:5000/api/cities
def api_cities():
    db = get_db()
    rows = db.execute('SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid, rating, rated FROM cities ORDER BY added_on DESC').fetchall()
    return jsonify([dict(row) for row in rows])

@api.route('/cities/<int:city_id>', methods=["GET"]) # curl http://127.0.0.1:5000/api/cities/0
def api_city(city_id):
    db = get_db()
    row = db.execute('SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid, rating, rated FROM cities WHERE id = ?', [city_id]).fetchone()
    if row is None:
        abort(404, description='City not found')
    return jsonify(dict(row))

@api.route('/cities/add', methods=['POST']) # curl -X POST -H "Content-Type: application/json" -d "{\"geonameid\": 0000000, \"name\":\"abcde\", \"rated\":0, \"rating\":0, \"visited\":0}" http://127.0.0.1:5000/api/cities/add
def api_add_city():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description='Missing data')
    if 'geonameid' not in data and 'name' not in data:
        abort(400, description='Missing geonameid or name in data')
    if 'visited' in data and data['visited'] not in [0,1,2]:
        abort(400, description='Incorrect visited data')
    if 'rating' in data and data['rating'] not in [0,1,2,3,4,5,6,7,8,9,10]:
        abort(400, description='Incorrect rating data')
    if 'rated' in data and data['rated'] not in [0,1]:
        abort(400, description='Incorrect rated data')
    db = get_db()
    if 'geonameid' in data:    
        city_geonameid = data['geonameid']
        existingCity = db.execute("SELECT id FROM cities WHERE geonameid = ?", [city_geonameid]).fetchone()
        if existingCity:
            abort(400, description='City already in database')
        city = find_city_by_id(city_geonameid)
    if 'name' in data:
        cities = find_cities(data['name'])
        city_name = data['name']
        existingCity = db.execute("SELECT id FROM cities WHERE name = ?", [city_name]).fetchone()
        if existingCity:
            abort(400, description='City already in database')
        city = cities[0]
    if 'geonameid' in data and 'name' in data:
        if city[5] != data['geonameid']:
            abort(400, description='geonameid and name point to a different city')
    if city is None:
        abort(400, description='City not found')
    if 'rated' in data:
        city.append(data['rated'])
    else:
        city.append(0)
    if 'rating' in data:
        city.append(data['rating'])
    else:
        city.append(0)
    if 'visited' in data:
        city.append(data['visited'])
    else:
        city.append(0)
    cur = db.execute('INSERT INTO cities(name, country, latitude, longitude, population, geonameid, rated, rating, visited) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', city)
    db.commit()
    city_id = cur.lastrowid
    row = db.execute('SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid, rating, rated FROM cities WHERE id = ?', [city_id]).fetchone()
    return jsonify(dict(row)), 201

@api.route('/cities/<int:city_id>', methods=["PUT", "PATCH"]) # curl -X PATCH -H "Content-Type: application/json" -d "{\"rated\":0, \"rating\":0, \"visited\":0}" http://127.0.0.1:5000/api/cities/0
def api_update_city(city_id):
    db = get_db()
    city = db.execute('SELECT name FROM cities WHERE id = ?', [city_id]).fetchone()
    if city is None:
        abort(404, description='City not found')
    data = request.get_json(silent=True)
    if not 'visited' in data and not 'rated' in data and not 'rating' in data:
        abort(404, description='No changeble data provided')
    if 'visited' in data and data['visited'] not in [0,1,2]:
        abort(400, description='Incorrect visited data')
    if 'rating' in data and data['rating'] not in [0,1,2,3,4,5,6,7,8,9,10]:
        abort(400, description='Incorrect rating data')
    if 'rated' in data and data['rated'] not in [0,1]:
        abort(400, description='Incorrect rated data')
    if 'visited' in data:
        db.execute('UPDATE cities SET visited = ? WHERE id = ?', [data['visited'], city_id])
        db.commit()
    if 'rating' in data:
        db.execute('UPDATE cities SET rating = ? WHERE id = ?', [data['rating'], city_id])
        db.commit()
    if 'rated' in data:
        db.execute('UPDATE cities SET rated = ? WHERE id = ?', [data['rated'], city_id])
        db.commit()
    row = db.execute('SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid, rating, rated FROM cities WHERE id = ?', [city_id]).fetchone()
    return jsonify(dict(row))
    
@api.route('/cities/<int:city_id>', methods=["DELETE"]) # curl -X DELETE http://127.0.0.1:5000/api/cities/0
def api_delete_city(city_id):
    db = get_db()
    city = db.execute('SELECT name FROM cities WHERE id = ?', [city_id]).fetchone()
    if city is None:
        abort(404, description='No city to remove')
    db.execute("DELETE FROM cities WHERE id = ?", [city_id])
    db.commit()
    return "", 204