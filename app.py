from flask import Flask, request, send_file
import xml.etree.ElementTree as ET
import csv
import os

app = Flask(__name__)

@app.route("/api/convert", methods=["POST"])
def convert_gpx_to_poi():
    if "file" not in request.files:
        return "Geen bestand geüpload", 400
    
    file = request.files["file"]
    if file.filename == "":
        return "Leeg bestand", 400
    
    # Parse GPX
    tree = ET.parse(file)
    root = tree.getroot()

    # Correcte namespaces voor GPX 1.0
    ns = {
        "gpx": "http://www.topografix.com/GPX/1/0",
        "groundspeak": "http://www.groundspeak.com/cache/1/0/1"
    }

    # Log het root-element om de structuur te zien
    print(f"Root Element: {root.tag}")

    poi_data = []
    waypoints_found = 0

    # Zoek naar waypoints in de nieuwe namespace
    for wpt in root.findall(".//{http://www.topografix.com/GPX/1/0}wpt"):
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        
        # Naam en beschrijving uit de GPX zelf
        name = wpt.find("{http://www.topografix.com/GPX/1/0}name")
        desc = wpt.find("{http://www.topografix.com/GPX/1/0}desc")
        
        # Extra geocache informatie uit Groundspeak
        cache_name = wpt.find("{http://www.groundspeak.com/cache/1/0/1}name")
        cache_desc = wpt.find("{http://www.groundspeak.com/cache/1/0/1}long_description")

        # Controleer of we waypoints vinden
        if name is not None and lat and lon:
            waypoints_found += 1
            poi_data.append([
                cache_name.text if cache_name is not None else (name.text if name is not None else "Onbekend"),
                lat,
                lon,
                cache_desc.text if cache_desc is not None else (desc.text if desc is not None else "Geen beschrijving")
            ])

    # Log het aantal gevonden waypoints
    print(f"Waypoints gevonden: {waypoints_found}")

    # Maak een CSV-bestand
    output_file = "converted_poi.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Naam", "Breedtegraad", "Lengtegraad", "Beschrijving"])
        writer.writerows(poi_data)

    # Als geen waypoints zijn gevonden, log dan een waarschuwing
    if waypoints_found == 0:
        print("Waarschuwing: Geen waypoints gevonden in het GPX-bestand!")

    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
