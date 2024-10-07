from flask import Flask, request, render_template, jsonify
import requests
import urllib.parse
from datetime import datetime, timedelta  # Import datetime for ETA calculation

app = Flask(__name__)

route_url = "https://graphhopper.com/api/1/route?"
key = "36c57771-b62a-41c7-a761-38bfb729be0c"

def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    
    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        return json_status, lat, lng, name
    else:
        return None, None, None, location

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/get_directions', methods=['POST'])
def get_directions():
    vehicle = request.form['vehicle']
    loc1 = request.form['start_loc']
    loc2 = request.form['dest_loc']
    optimization = request.form['optimization']  # 'fastest' or 'shortest'

    orig = geocoding(loc1, key)
    dest = geocoding(loc2, key)

    if orig[0] == 200 and dest[0] == 200:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])

        # Adjust route parameters based on optimization selection
        if optimization == 'shortest':
            optimize_param = '&optimize=false'  # Shortest route
        else:
            optimize_param = '&optimize=true'  # Fastest route (default)

        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle}) + op + dp + optimize_param
        paths_data = requests.get(paths_url).json()

        if requests.get(paths_url).status_code == 200:
            directions = f"Directions from {orig[3]} to {dest[3]}:\n"
            miles = paths_data["paths"][0]["distance"] / 1000 / 1.61 
            km = paths_data["paths"][0]["distance"] / 1000
            time = int(paths_data["paths"][0]["time"] / 1000 / 60)  # in minutes
            directions += f"Distance: {km:.1f} km ({miles:.1f} miles)\nDuration: {time} minutes\n\n"
            
            # Calculate ETA
            current_time = datetime.now()  # Get current time
            eta = current_time + timedelta(minutes=time)  # Add travel time to current time
            eta_formatted = eta.strftime("%I:%M %p")  # Format ETA as HH:MM AM/PM

            directions += f"Estimated Arrival Time (ETA): {eta_formatted}\n\n"

            steps = []
            for step in paths_data["paths"][0]["instructions"]:
                steps.append(f"{step['text']} ({step['distance']/1000:.1f} km)")

            return jsonify({'directions': directions, 'steps': steps})
        else:
            return jsonify({'error': paths_data["message"]})
    else:
        return jsonify({'error': 'Invalid origin or destination'})

@app.route('/suggestions')
def suggestions():
    query = request.args.get('query')
    type = request.args.get('type')

    # Geocoding URL to get location suggestions
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": query, "limit": "5", "key": key})  # Limit to 5 suggestions
    replydata = requests.get(url)
    json_data = replydata.json()
    
    suggestions = []
    if replydata.status_code == 200 and len(json_data["hits"]) > 0:
        suggestions = [hit["name"] for hit in json_data["hits"]]

    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
