from flask import Flask, jsonify, render_template
import subprocess
import json

app = Flask(__name__)

def get_location():
    result = subprocess.run(['termux-location'], stdout=subprocess.PIPE)
    location_data = json.loads(result.stdout.decode('utf-8'))
    return location_data

@app.route('/location')
def location():
    location_data = get_location()
    return jsonify(location_data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    