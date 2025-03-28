from flask import Flask, request, send_file, Response
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

    # Namespaces gebruiken als nodig
    ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
    
    poi_data = []
    waypoints_found = 0  # Debug teller

    for wpt in root.findall("gpx:wpt", ns):
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        name = wpt.find("gpx:name", ns)
        desc = wpt.find("gpx:desc", ns)
        
        poi_data.append([name.text if name is not None else "Onbekend", lat, lon, desc.text if desc is not None else ""])
        waypoints_found += 1  # Debug teller

    print(f"Waypoints gevonden: {waypoints_found}")  # Log het aantal waypoints

    # Maak een CSV-bestand
    output_file = "converted_poi.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Naam", "Breedtegraad", "Lengtegraad", "Beschrijving"])
        writer.writerows(poi_data)

    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
