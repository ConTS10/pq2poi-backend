from flask import Flask, request, send_file
import xml.etree.ElementTree as ET
from io import BytesIO

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
    
    # Maak een nieuwe GPX-root voor de POI's
    gpx_ns = {"gpx": "http://www.topografix.com/GPX/1/1"}
    new_root = ET.Element("gpx", version="1.1", creator="PQ2POI", xmlns="http://www.topografix.com/GPX/1/1")
    
    # Voeg een naamruimte toe aan de root
    tree = ET.ElementTree(new_root)
    
    # Voeg de waypoints toe aan de nieuwe GPX
    for wpt in root.findall("gpx:wpt", ns):
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        name = wpt.find("gpx:name", ns)
        desc = wpt.find("gpx:desc", ns)
        
        waypoint = ET.SubElement(new_root, "wpt", lat=lat, lon=lon)
        
        if name is not None:
            ET.SubElement(waypoint, "name").text = name.text
        if desc is not None:
            ET.SubElement(waypoint, "desc").text = desc.text

    # Zet de nieuwe GPX om naar een bestand in geheugen
    output = BytesIO()
    tree.write(output, encoding="utf-8", xml_declaration=True)
    output.seek(0)
    
    # Zorg ervoor dat het bestand gedownload wordt
    return send_file(output, as_attachment=True, download_name="converted_poi.gpx", mimetype="application/gpx+xml")

if __name__ == "__main__":
    app.run(debug=True)
