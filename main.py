from flask import Flask, jsonify, render_template
import subprocess
import json
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

app = Flask(__name__)

def get_location_from_termux():
    try:
        result = subprocess.run(['termux-location'], stdout=subprocess.PIPE, timeout=6)
        output = result.stdout.decode('utf-8')
        print(f"termux-location output: {output}")  # Debugging output
        if output.strip():  # Ensure result is not empty
            location_data = json.loads(output)
            if location_data.get('latitude') and location_data.get('longitude'):
                location_data['provider'] = 'termux-location'
                return location_data
    except subprocess.TimeoutExpired:
        print("Error: termux-location command timed out.")
    except Exception as e:
        print(f"Error getting location from termux: {e}")
    return None

def get_cell_info():
    try:
        result = subprocess.run(['termux-telephony-cellinfo'], stdout=subprocess.PIPE, timeout=6)
        output = result.stdout.decode('utf-8')
        print(f"termux-telephony-cellinfo output: {output}")  # Debugging output
        if output.strip():  # Ensure result is not empty
            cell_info = json.loads(output)
            if cell_info and isinstance(cell_info, list):
                for cell in cell_info:
                    if 'type' in cell and cell['registered']:
                        return cell  # Return the first registered cell info
    except subprocess.TimeoutExpired:
        print("Error: termux-telephony-cellinfo command timed out.")
    except Exception as e:
        print(f"Error getting cell info: {e}")
    return None

def get_location_from_opencellid(cell_info):
    api_key = 'pk.f539d23198812c26386f412cc357b792'
    url = f'https://us1.unwiredlabs.com/v2/process.php'
    payload = {
        'token': api_key,
        'radio': cell_info['type'],
        'mcc': cell_info['mcc'],
        'mnc': cell_info['mnc'],
        'cells': [{
            'lac': cell_info['tac'],
            'cid': cell_info['ci']
        }],
        'address': 1
    }
    print(f"OpenCellID request payload: {payload}")  # Debugging output
    try:
        response = requests.post(url, json=payload, verify=False, timeout=10)  # Set timeout to 10 seconds
        print(f"OpenCellID response status: {response.status_code}")  # Debugging output
        if response.status_code == 200:
            data = response.json()
            print(f"OpenCellID response data: {data}")  # Debugging output
            if 'lat' in data and 'lon' in data:
                return {
                    'latitude': data['lat'],
                    'longitude': data['lon'],
                    'altitude': 0,
                    'accuracy': data.get('accuracy', None),
                    'vertical_accuracy': None,
                    'bearing': None,
                    'speed': None,
                    'elapsedMs': None,
                    'provider': 'opencellid'
                }
    except Exception as e:
        print(f"Error getting location from OpenCellID: {e}")
    return None

def get_location_from_ip():
    try:
        response = requests.get('http://ip-api.com/json/', timeout=10)  # Set timeout to 10 seconds
        if response.status_code == 200:
            data = response.json()
            return {
                'latitude': data['lat'],
                'longitude': data['lon'],
                'altitude': 0,
                'accuracy': data.get('accuracy', None),
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
        cell_info = get_cell_info()
        print(f"Cell info: {cell_info}")  # Debugging output
        if cell_info:
            location_data = get_location_from_opencellid(cell_info)
    if not location_data:
        location_data = get_location_from_ip()
    return jsonify(location_data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    app.run(debug=True, host='0.0.0.0', port=5530)
