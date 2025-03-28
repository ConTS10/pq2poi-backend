from flask import Flask, request, send_file
from flask_cors import CORS  # Importeer CORS
import xml.etree.ElementTree as ET
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Sta CORS toe voor de hele app

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

    # Zoek naar de versie van de namespace
    ns = {}
    if "{http://www.topografix.com/GPX/1/1}gpx" in root.tag:
        ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
    elif "{http://www.topografix.com/GPX/1/0}gpx" in root.tag:
        ns = {"gpx": "http://www.topografix.com/GPX/1/0"}
    
    # Maak een nieuwe GPX-root voor de POI's
    new_root = ET.Element("gpx", version="1.1", creator="PQ2POI", xmlns="http://www.topografix.com/GPX/1/1")
    
    # Debugging: controleer het originele bestand
    print("Root Element:", root.tag)
    
    # Voeg de waypoints toe aan de nieuwe GPX
    waypoints_added = 0
    for wpt in root.findall("gpx:wpt", ns):
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        name = wpt.find("gpx:name", ns)
        desc = wpt.find("gpx:desc", ns)
        
        # Voeg waypoint toe aan de nieuwe root
        waypoint = ET.SubElement(new_root, "wpt", lat=lat, lon=lon)
        
        # Voeg name en desc toe als ze aanwezig zijn
        if name is not None:
            ET.SubElement(waypoint, "name").text = name.text
        if desc is not None:
            ET.SubElement(waypoint, "desc").text = desc.text
        
        waypoints_added += 1
    
    # Debugging: controleer het aantal gevonden waypoints
    print(f"Waypoints gevonden: {waypoints_added}")
    
    if waypoints_added == 0:
        print("Waarschuwing: Geen waypoints gevonden in het GPX-bestand!")
    
    # Zet de nieuwe GPX om naar een bestand in geheugen
    output = BytesIO()
    tree = ET.ElementTree(new_root)  # We gebruiken de nieuwe root voor de ElementTree
    tree.write(output, encoding="utf-8", xml_declaration=True)
    output.seek(0)
    
    # Zorg ervoor dat het bestand gedownload wordt
    return send_file(output, as_attachment=True, download_name="converted_poi.gpx", mimetype="application/gpx+xml")

if __name__ == "__main__":
    app.run(debug=True)
