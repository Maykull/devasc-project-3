from flask import Flask, render_template, request, redirect, url_for
import requests
import urllib.parse

app = Flask(__name__)

route_url = "https://graphhopper.com/api/1/route?"
key = "3f75d86d-495e-4b06-ac45-d30bd9d7c821"  # Replace with your API key

# Helper function for geocoding
def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data["hits"]:
        lat = data["hits"][0]["point"]["lat"]
        lng = data["hits"][0]["point"]["lng"]
        return lat, lng, data["hits"][0].get("name", "")
    else:
        return None, None, ""

# Flask Routes
@app.route("/")
def root():
    return redirect(url_for('welcome'))

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/mapquest", methods=["GET", "POST"])  # Changed to /mapquest
def index():
    if request.method == "POST":
        start_loc = request.form.get("start_location")
        dest_loc = request.form.get("destination")
        vehicle_profile = request.form.get("vehicle_profile")
        
        start_lat, start_lng, start_name = geocoding(start_loc, key)
        dest_lat, dest_lng, dest_name = geocoding(dest_loc, key)
        
        if start_lat and dest_lat:
            # Build Route URL
            op = f"&point={start_lat},{start_lng}"
            dp = f"&point={dest_lat},{dest_lng}"
            route = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle_profile}) + op + dp
            
            # Fetch route data
            route_response = requests.get(route)
            route_data = route_response.json()

            if route_response.status_code == 200:
                distance_km = route_data["paths"][0]["distance"] / 1000
                distance_miles = distance_km / 1.61
                duration_sec = route_data["paths"][0]["time"] / 1000
                instructions = route_data["paths"][0]["instructions"]
                
                return render_template("index.html", 
                                       start=start_name, dest=dest_name, 
                                       distance_km=distance_km, distance_miles=distance_miles, 
                                       duration_sec=duration_sec, instructions=instructions)
            else:
                return render_template("index.html", error="Failed to fetch route.")
        else:
            return render_template("index.html", error="Invalid location.")
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
