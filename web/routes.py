from flask import Blueprint, render_template, redirect, url_for, request, flash
from outsideapi.outsideapi import find_city_by_id, find_cities, list_countries, biggest_cities_in_country, get_country_id
from db import get_db
from web.helpers import city_add

web = Blueprint('web', __name__)


@web.route('/')
def index():
    db = get_db()
    cities = db.execute('SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid FROM cities ORDER BY population DESC').fetchall()
    city_cords = []
    for city in cities:
        lat = float(city['latitude'])
        lng = float(city['longitude'])
        adj_lng = ((((lng+169.6)%360 + 360)%360)/360)*100
        lat = max(min(lat,84.5), -57)
        adj_lat = ((84.5-lat)/142.5)*100
        city_cords.append([city['id'], city['name'], adj_lat, adj_lng, city['visited']])
    return render_template('index.html', cities = cities, city_cords=city_cords)

@web.route('/tracked')
def tracked():
    db = get_db()
    cities = db.execute('SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid FROM cities ORDER BY population DESC').fetchall()
    return render_template('tracked.html', cities = cities)

@web.route('/tracked/<int:city_id>', methods=["POST", "GET"])
def city(city_id):
    db = get_db()
    city = db.execute("SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid, rating, rated FROM cities WHERE id = ?", [city_id]).fetchone()
    url = f'{city['country']}.jpg'
    see_change_status = 0
    see_change_rating = 0
    if request.method == "POST":
        if 'see_change_status' in request.form:
            see_change_status = int(request.form.get('see_change_status'))
        elif 'see_change_rating' in request.form:
            see_change_rating = int(request.form.get('see_change_rating'))

    return render_template("city.html", city = city, url=url, see_change_status=see_change_status, see_change_rating=see_change_rating)

@web.route('/tracked/<int:city_id>/rate', methods=["POST", "GET"])
def rate(city_id):
    if request.method == "POST":
        rating = request.form.get('rating')
        db = get_db()
        db.execute('UPDATE cities SET rated = 1, rating = ? WHERE id = ?', [rating, city_id])
        db.commit()
        flash('Rating added')
        return redirect(url_for('web.city', city_id=city_id))
    
@web.route('/tracked/<int:city_id>/remove_rating', methods = ["POST", "GET"])
def remove_rating(city_id):
    if request.method == "POST":
        db = get_db()
        db.execute('UPDATE cities SET rated = 0, rating = 0 WHERE id = ?', [city_id])
        db.commit()
        flash('Removed rating')
        return redirect(url_for('web.city', city_id=city_id))

@web.route('/tracked/<int:city_id>/delete', methods=["POST"])
def delete_city(city_id):
    db = get_db()
    name = db.execute("SELECT name FROM cities WHERE id = ?", [city_id]).fetchone()
    db.execute("DELETE FROM cities WHERE id = ?", [city_id])
    db.commit()
    flash(f"Stopped tracking {name["name"]}")
    return redirect(url_for('web.tracked'))

@web.route('/tracked/<int:city_id>/status', methods=["POST", "GET"])
def change_status(city_id):
    if request.method == "POST":
        new_status = request.form.get("status")
        db = get_db()
        if new_status == 'visited':
            db.execute("UPDATE cities SET visited = 2 WHERE id = ?", [city_id])
            db.commit()
            flash("status set to visited")
        elif new_status == 'planned':
            db.execute("UPDATE cities SET visited = 1 WHERE id = ?", [city_id])
            db.commit()
            flash("status set to planned")
        elif new_status == 'not_visited':
            db.execute("UPDATE cities SET visited = 0 WHERE id = ?", [city_id])
            db.commit()
            flash("status set to not visited")
        return redirect(url_for('web.city', city_id = city_id))
        
@web.route('/countries')
def countries():
    countries = list_countries()
    countries.sort()
    return render_template('countries.html', countries=countries)

@web.route('/countries/<country_name>', methods=["POST", "GET"])
def country(country_name):
    biggest_cities = biggest_cities_in_country(country_name)
    db = get_db()
    tracked_cities = db.execute("SELECT id, name, visited, added_on, latitude, longitude, country, population, geonameid FROM cities WHERE country = ?", [country_name]).fetchall()
    len_tracked_cities = len(tracked_cities)
    tracked_ids = {}
    for city in tracked_cities:
        tracked_ids[city['geonameid']] = city['id']
    if request.method == "POST":
        id = request.form.get('id')
        city = find_city_by_id(id)
        city_add(city)
        return redirect(url_for('web.country', country_name=country_name))
    country_id = get_country_id(country_name)
    return render_template('country.html', country=country_name, biggest_cities=biggest_cities, tracked_cities=tracked_cities, length=len_tracked_cities, tracked_ids=tracked_ids, country_id=country_id)

@web.route('/ratings')
def ratings():
    db = get_db()
    rated_cities = db. execute('SELECT id, name, country, rating FROM cities WHERE rated = 1 ORDER BY rating DESC').fetchall()
    return render_template('ratings.html', rated_cities = rated_cities) 

@web.route('/add_city', methods=['POST', 'GET'])
def add_city():
    multiple_choice = False
    citiesList = []
    if request.method == 'POST':
        if 'name' in request.form:
            name = request.form.get("name").strip()
            citiesList = find_cities(name)
            if len(citiesList) == 0:
                flash("City not found.")
                return render_template('add_city.html', multiple_choice=multiple_choice, citiesList=citiesList)
            db = get_db()
            if len(citiesList) == 1:
                city = citiesList[0]
                if city_add(city) == 'city exists':
                    flash("City already added.")
                    return render_template('add_city.html', multiple_choice=multiple_choice, citiesList=citiesList)
                return render_template('add_city.html', multiple_choice=multiple_choice, citiesList=citiesList)
            if len(citiesList) > 1:
                multiple_choice = True
                flash(f"Multiple cities called {name} found. Pick one:")
                return render_template('add_city.html', multiple_choice=multiple_choice, citiesList=citiesList)
        elif 'id' in request.form:    
            id = request.form.get('id')
            city = find_city_by_id(id)
            if city_add(city) == 'city exists':
                flash("City already added.")
                return render_template('add_city.html', multiple_choice=multiple_choice, citiesList=citiesList)
            return render_template('add_city.html', multiple_choice=multiple_choice, citiesList=citiesList)
    return render_template('add_city.html', multiple_choice=multiple_choice, citiesList=citiesList)
