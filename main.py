from flask import Flask, jsonify, render_template
import subprocess
import json
import requests

app = Flask(__name__)

def get_location_from_termux():
    try:
        result = subprocess.run(['termux-location'], stdout=subprocess.PIPE, timeout=10)
        location_data = json.loads(result.stdout.decode('utf-8'))
        if location_data.get('latitude') and location_data.get('longitude'):
            return location_data
    except Exception as e:
        print(f"Error getting location from termux: {e}")
    return None

def get_location_from_ip():
    try:
        response = requests.get('http://ip-api.com/json/')
        if response.status_code == 200:
            data = response.json()
            return {
                'latitude': data['lat'],
                'longitude': data['lon'],
                'altitude': 0,
                'accuracy': data['accuracy'] if 'accuracy' in data else None,
                'vertical_accuracy': None,
                'bearing': None,
                'speed': None,
                'elapsedMs': None,
                'provider': 'ip-api'
            }
    except Exception as e:
        print(f"Error getting location from IP: {e}")
    return None

@app.route('/location')
def location():
    location_data = get_location_from_termux()
    if not location_data:
        location_data = get_location_from_ip()
    return jsonify(location_data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
