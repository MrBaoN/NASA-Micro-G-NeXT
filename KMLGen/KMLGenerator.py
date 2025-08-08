import simplekml
import os
import json
import sys
import datetime

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <fifo_path>")
    sys.exit(1)

# Create the KML object once, outside the loop
kml = simplekml.Kml()

# Generate filename once when script starts
os.makedirs("kmls", exist_ok=True)
output_file = f"kmls/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.kml"

with open(sys.argv[1], 'r') as fifo:
    while True:
        data = fifo.readline()
        if data:
            if data[-1] == '\n':
                data = data[:-1]
            print(data)
            try:
                received = json.loads(data)
                print(f"\nReceived:")
                print(received)
                print(received.get('latMinute'))
                
                latitude = float(received['finalLat']) * -1
                longitude = float(received['finalLong']) * -1
                latitude = latitude if (received.get('latDirection') == '0') else -latitude
                longitude = longitude if (received.get('longDirection') == '0') else -longitude
                print('location is', latitude,',',longitude)
                
                # Add point to existing KML object instead of creating new one
                point = kml.newpoint(name=f"Coordinate Data", coords=[(longitude, latitude)])  
                
                # Write the complete KML (same filename each time)
                kml.save(output_file)
                print(f"KML file '{output_file}' has been updated.")
                
            except json.JSONDecodeError:
                print("Invalid JSON received")
