from flask import Flask, request, render_template, jsonify
import requests
import urllib.parse
from datetime import datetime, timedelta

# Initialize the Flask app
app = Flask(__name__)

# GraphHopper API route and key
route_url = "https://graphhopper.com/api/1/route?"
key = "36c57771-b62a-41c7-a761-38bfb729be0c"

# Geocoding function to get latitude and longitude from location name
def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    
    # Check if geocoding was successful
    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        return json_status, lat, lng, name
    else:
        return None, None, None, location

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
    vehicle = request.form['vehicle']
    loc1 = request.form['start_loc']
    loc2 = request.form['dest_loc']
    optimization = request.form['optimization']

    # Get geocoding data for start and destination
    orig = geocoding(loc1, key)
    dest = geocoding(loc2, key)

    # Ensure geocoding succeeded for both locations
    if orig[0] == 200 and dest[0] == 200:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])

        # Use shortest or fastest route based on user selection
        optimize_param = '&optimize=false' if optimization == 'shortest' else '&optimize=true'
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp + optimize_param
        paths_data = requests.get(paths_url).json()

        if requests.get(paths_url).status_code == 200:
            directions = f"Directions from {orig[3]} to {dest[3]}:\n"
            miles = paths_data["paths"][0]["distance"] / 1000 / 1.61
            km = paths_data["paths"][0]["distance"] / 1000
            time = int(paths_data["paths"][0]["time"] / 1000 / 60)
            directions += f"Distance: {km:.1f} km ({miles:.1f} miles)\nDuration: {time} minutes\n\n"
            
            # Calculate Estimated Time of Arrival (ETA)
            current_time = datetime.now()
            eta = current_time + timedelta(minutes=time)
            eta_formatted = eta.strftime("%I:%M %p")
            directions += f"Estimated Arrival Time (ETA): {eta_formatted}\n\n"

            # Collect step-by-step directions
            steps = [f"{step['text']} ({step['distance']/1000:.1f} km)" for step in paths_data["paths"][0]["instructions"]]

            return jsonify({'directions': directions, 'steps': steps})
        else:
            return jsonify({'error': paths_data["message"]})
    else:
        return jsonify({'error': 'Invalid origin or destination'})

# Route for location suggestions
@app.route('/suggestions')
def suggestions():
    query = request.args.get('query')
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": query, "limit": "5", "key": key})
    
    replydata = requests.get(url)
    json_data = replydata.json()
    
    # Extract and return location suggestions
    suggestions = [hit["name"] for hit in json_data["hits"]] if replydata.status_code == 200 else []
    
    return jsonify(suggestions)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
