from flask import Flask, request, render_template, jsonify
import requests
import urllib.parse
import polyline  # For decoding encoded points

# Initialize the Flask app
app = Flask(__name__)

# GraphHopper API key
key = "fe27fd23-2c23-4019-a2b3-e316d862a3a1"
# Open-Meteo Weather API base URL
weather_api_base_url = "https://api.open-meteo.com/v1/forecast"

# Geocoding function to get latitude and longitude from location name
def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    
    response = requests.get(url)
    json_data = response.json()
    status_code = response.status_code
    
    if status_code == 200 and json_data.get("hits"):
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        return lat, lng, name
    else:
        return None, None, location

# Weather-fetching function
def fetch_weather(lat, lng):
    try:
        # Fetch weather data from Open-Meteo API
        weather_url = f"{weather_api_base_url}?latitude={lat}&longitude={lng}&current_weather=true"
        response = requests.get(weather_url)
        weather_data = response.json()
        
        if 'current_weather' in weather_data:
            current_weather = weather_data['current_weather']
            return {
                "temperature": current_weather.get("temperature"),
                "wind_speed": current_weather.get("windspeed"),
                "weather_code": current_weather.get("weathercode"),
                "time": current_weather.get("time"),
            }
        else:
            return {"error": "Weather data not available"}
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {"error": "Failed to fetch weather data"}

# Route for the welcome page
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Route for the index page
@app.route('/index')
def index():
    return render_template('index.html')

# Route for fetching directions
@app.route('/get_directions', methods=['POST'])
def get_directions():
    try:
        vehicle = request.form.get('vehicle', 'car')
        start_loc = request.form.get('start_loc')
        dest_loc = request.form.get('dest_loc')

        # Geocode start and destination locations
        start_lat, start_lng, start_name = geocoding(start_loc, key)
        if not start_lat or not start_lng:
            return jsonify({'error': f"Failed to geocode start location: {start_loc}"}), 400

        end_lat, end_lng, end_name = geocoding(dest_loc, key)
        if not end_lat or not end_lng:
            return jsonify({'error': f"Failed to geocode destination: {dest_loc}"}), 400

        # Fetch weather for start and destination
        start_weather = fetch_weather(start_lat, start_lng)
        end_weather = fetch_weather(end_lat, end_lng)

        # Prepare request to GraphHopper
        start_coords = f"{start_lat},{start_lng}"
        end_coords = f"{end_lat},{end_lng}"
        route_url = f"https://graphhopper.com/api/1/route?key={key}&point={start_coords}&point={end_coords}&vehicle={vehicle}"

        response = requests.get(route_url)
        paths_data = response.json()

        if "paths" not in paths_data or not paths_data["paths"]:
            return jsonify({'error': 'No routes found in the API response.'}), 500

        # Decode the polyline
        encoded_points = paths_data["paths"][0]["points"]
        geometry = polyline.decode(encoded_points)

        # Extract instructions (steps)
        steps = [
            {"text": step["text"], "distance": step["distance"]}
            for step in paths_data["paths"][0]["instructions"]
        ]

        directions = f"Route from {start_name} to {end_name}"
        return jsonify({
            'directions': directions,
            'steps': steps,
            'geometry': geometry,
            'start_weather': start_weather,
            'end_weather': end_weather
        })

    except Exception as e:
        print(f"Error in /get_directions: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

# Route for location suggestions
@app.route('/suggestions')
def suggestions():
    query = request.args.get('query')
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": query, "limit": "5", "key": key})
    
    response = requests.get(url)
    json_data = response.json()
    
    suggestions = [hit["name"] for hit in json_data.get("hits", [])]
    return jsonify(suggestions)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
