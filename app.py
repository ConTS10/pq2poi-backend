from flask import Flask, request, send_file
import xml.etree.ElementTree as ET
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/convert", methods=["POST"])
def convert_gpx_to_poi():
    if "file" not in request.files:
        return "Geen bestand geüpload", 400
    
    file = request.files["file"]
    if file.filename == "":
        return "Leeg bestand", 400
    
    # Parse GPX bestand
    tree = ET.parse(file)
    root = tree.getroot()

    # Haal de standaard namespace op
    namespace = {"gpx": "http://www.topografix.com/GPX/1/0"}

    # Zoek naar waypoints binnen deze namespace
    waypoints = root.findall("gpx:wpt", namespace)

    print(f"Aantal waypoints gevonden: {len(waypoints)}")  # Debugging

    if not waypoints:
        return "Geen waypoints gevonden in het GPX-bestand!", 400
    
    # Voor elke waypoint de gegevens verzamelen
    poi_data = []
    for wpt in waypoints:
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        name = wpt.find("gpx:name", namespace)
        desc = wpt.find("gpx:desc", namespace)
        
        poi_data.append({
            "name": name.text if name is not None else "Onbekend",
            "lat": lat,
            "lon": lon,
            "desc": desc.text if desc is not None else ""
        })
    
    # Maak het nieuwe GPX bestand aan
    gpx_data = ET.Element("gpx", version="1.1", creator="PQ2POI", xmlns="http://www.topografix.com/GPX/1/1")

    for poi in poi_data:
        wpt = ET.SubElement(gpx_data, "wpt", lat=poi["lat"], lon=poi["lon"])
        name = ET.SubElement(wpt, "name")
        name.text = poi["name"]
        desc = ET.SubElement(wpt, "desc")
        desc.text = poi["desc"]

    # Mooi geformatteerd XML-bestand opslaan
    gpx_str = ET.tostring(gpx_data, encoding="utf-8", method="xml").decode("utf-8")
    gpx_str = "\n".join([line.strip() for line in gpx_str.splitlines()])

    output_file = "converted_poi.gpx"
    
    response = send_file(
        output_file,
        mimetype="application/gpx+xml",
        as_attachment=True,
        download_name="converted_poi.gpx"
    )
    response.set_data(gpx_str.encode("utf-8"))
    return response

if __name__ == "__main__":
    app.run(debug=True)
