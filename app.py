from flask import Flask, request, send_file
from flask_cors import CORS
import xml.etree.ElementTree as ET
import tempfile

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

    # Gebruik de juiste namespace {http://www.topografix.com/GPX/1/0}
    ns = {"gpx": "http://www.topografix.com/GPX/1/0"}

    # Maak een nieuw GPX-bestand aan
    new_gpx = ET.Element("gpx", version="1.1", creator="PQ2POI", xmlns="http://www.topografix.com/GPX/1/1")

    # Loop door alle waypoints en voeg ze toe
    for wpt in root.findall("gpx:wpt", ns):
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        name = wpt.find("gpx:name", ns)
        desc = wpt.find("gpx:desc", ns)
        
        # Maak een nieuw waypoint element
        wpt_element = ET.SubElement(new_gpx, "wpt", lat=lat, lon=lon)
        if name is not None:
            ET.SubElement(wpt_element, "name").text = name.text
        if desc is not None:
            ET.SubElement(wpt_element, "desc").text = desc.text
    
    # Genereer een tijdelijk bestand om de GPX in op te slaan
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as tmp_file:
        tree = ET.ElementTree(new_gpx)
        tree.write(tmp_file, encoding="utf-8", xml_declaration=True)

        tmp_file.close()
        # Stuur het bestand als antwoord
        return send_file(tmp_file.name, as_attachment=True, download_name="converted_poi.gpx", mimetype="application/gpx+xml")

if __name__ == "__main__":
    app.run(debug=True)
