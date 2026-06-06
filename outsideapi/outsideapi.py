import requests
from requests.exceptions import RequestException

def find_city(city_name):
    try:
        parameters = {
            'name_equals': city_name,
            'featureClass': 'P',
            'username': 'matiw'
        }

        response = requests.get("http://api.geonames.org/searchJSON?", params = parameters)
        cities = response.json()

        if cities['totalResultsCount'] == 0:
            return 'no such city'
        elif cities['totalResultsCount'] == 1:
            city = cities['geonames'][0]
            return [city['toponymName'], city['countryName'], city['lat'], city['lng'], city['population'], city['geonameId']]
        else:
            namedCities = cities['geonames']
            namedCities.sort(key = lambda x: x['population'], reverse=True)
            city = namedCities[0]
            return [city['toponymName'], city['countryName'], city['lat'], city['lng'], city['population'], city['geonameId']] 
    except RequestException as e:
        return f'Error {e}'

def find_cities(city_name):
    try:
        parameters = {
            'name_equals': city_name,
            'featureClass': 'P',
            'username': 'matiw'
        }

        response = requests.get("http://api.geonames.org/searchJSON?", params = parameters)
        cities = response.json()

        if cities['totalResultsCount'] == 0:
            return []
        elif cities['totalResultsCount'] == 1:
            city = cities['geonames'][0]
            return [[city['toponymName'], city['countryName'], city['lat'], city['lng'], city['population'], city['geonameId']]]
        else:
            namedCities = cities['geonames']
            namedCities.sort(key = lambda x: x['population'], reverse=True)
            cityList = []
            for city in namedCities:
                cityList.append([city['toponymName'], city['countryName'], city['lat'], city['lng'], city['population'], city['geonameId']])
            return cityList
    except RequestException as e:
        return f'Error {e}'

def find_city_by_id(city_id):
    try:
        parameters = {
            'geonameId': city_id,
            'featureClass': 'P',
            'username': 'matiw'
        }
        response = requests.get("http://api.geonames.org/getJSON?", params = parameters)
        city = response.json()
        try: 
            result = [city['toponymName'], city['countryName'], city['lat'], city['lng'], city['population'], city['geonameId']]
        except KeyError:
            result = None
        return result
    except RequestException as e:
        return f'Error {e}'

def list_countries():
    try:
        parameters = {
            'featureCode': 'PCLI',
            'maxRows': 200,
            'username': 'matiw'
        }
        response = requests.get("http://api.geonames.org/searchJSON?", params = parameters)
        countries = response.json()
        country_names = []
        for country in countries['geonames']:
            country_names.append(country['name'])
        return country_names
    except RequestException as e:
        return f'Error {e}'

def get_country_id(country_name):
    try:
        parameters = {
            'featureCode': 'PCLI',
            'maxRows': 200,
            'username': 'matiw'
        }
        response = requests.get("http://api.geonames.org/searchJSON?", params = parameters)
        countries = response.json()
        country_id = {}
        for country in countries['geonames']:
            country_id[country['name']] = country['countryCode']
        return country_id[country_name]
    except RequestException as e:
        return f'Error {e}'

def biggest_cities_in_country(country_name):
    try:
        parameters = {
            'country': get_country_id(country_name),
            'maxRows': 10,
            'featureClass': 'P',
            'orderby': 'population',
            'username': 'matiw'
        }
        response = requests.get("http://api.geonames.org/searchJSON?", params = parameters)
        data = response.json()
        cities = []
        for city in data['geonames']:
            cities.append([city['toponymName'], city['countryName'], city['lat'], city['lng'], city['population'], city['geonameId']])
        return cities
    except RequestException as e:
        return f'Error {e}'


if __name__ == '__main__':
        print(get_country_id('China'))

