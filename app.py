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

    # Definieer namespaces
    ns = {
        "gpx": "http://www.topografix.com/GPX/1/1",
        "groundspeak": "http://www.groundspeak.com/cache/1/0/1"
    }

    poi_data = []
    for wpt in root.findall(".//{http://www.topografix.com/GPX/1/1}wpt"):
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        
        # Naam en beschrijving uit de GPX zelf
        name = wpt.find("{http://www.topografix.com/GPX/1/1}name")
        desc = wpt.find("{http://www.topografix.com/GPX/1/1}desc")
        
        # Extra geocache informatie uit Groundspeak
        cache_name = wpt.find("{http://www.groundspeak.com/cache/1/0/1}name")
        cache_desc = wpt.find("{http://www.groundspeak.com/cache/1/0/1}long_description")

        # Voeg de gevonden gegevens toe aan de lijst
        poi_data.append([
            cache_name.text if cache_name is not None else (name.text if name is not None else "Onbekend"),
            lat,
            lon,
            cache_desc.text if cache_desc is not None else (desc.text if desc is not None else "Geen beschrijving")
        ])

    # Maak een CSV-bestand
    output_file = "converted_poi.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Naam", "Breedtegraad", "Lengtegraad", "Beschrijving"])
        writer.writerows(poi_data)

    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
