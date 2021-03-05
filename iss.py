import requests
import json
from datetime import datetime
import geocoder

astro_url = 'http://api.open-notify.org/astros.json'
response = requests.get(astro_url)
astro_json = response.json()
print('Current ISS crew:\n')
for p in astro_json['people']:
    print(p['name'])

current_loc_url = 'http://api.open-notify.org/iss-now.json'
response = requests.get(current_loc_url)
loc_json = response.json()
lat = loc_json['iss_position'].get('latitude')
lon = loc_json['iss_position'].get('longitude')
g = geocoder.osm([lat, lon], method='reverse')
print(f"""
ISS currently over

Latitude {lat}, Longitude {lon}
{g.country}
{g.country_code.upper()}
{g.city}
{g.address}
""")

pass_time_url = 'http://api.open-notify.org/iss-pass.json'
parameters = {
    'lat': 51.51,
    'lon': -0.19
}
response = requests.get(pass_time_url, params=parameters)
pt_json = response.json()
print('ISS will pass over London at\n')
for pass_time in pt_json['response']:
    pt = datetime.fromtimestamp(pass_time['risetime'])
    time_delta = (pt - datetime.utcnow())
    print(f"{pt} ({str(time_delta)})")
