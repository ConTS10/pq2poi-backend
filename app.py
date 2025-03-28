from flask import Flask, request, send_file
from flask_cors import CORS
import xml.etree.ElementTree as ET
from io import BytesIO
import xml.dom.minidom

app = Flask(__name__)

# Functie om XML netjes op te maken met inspringing
def prettify_xml(element):
    # Zet de XML om in een string
    rough_string = ET.tostring(element, 'utf-8')
    # Maak het mooi op met behulp van minidom
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

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

    ns = {"gpx": "http://www.topografix.com/GPX/1/1"}

    # Maak een nieuw GPX-bestand
    gpx = ET.Element("gpx", version="1.1", creator="PQ2POI", xmlns="http://www.topografix.com/GPX/1/1")
    
    for wpt in root.findall("gpx:wpt", ns):
        lat = wpt.get("lat")
        lon = wpt.get("lon")
        name = wpt.find("gpx:name", ns)
        desc = wpt.find("gpx:desc", ns)

        # Voeg een waypoint toe aan de nieuwe GPX
        wpt_elem = ET.SubElement(gpx, "wpt", lat=lat, lon=lon)
        if name is not None:
            name_elem = ET.SubElement(wpt_elem, "name")
            name_elem.text = name.text
        if desc is not None:
            desc_elem = ET.SubElement(wpt_elem, "desc")
            desc_elem.text = desc.text

    # Maak het GPX bestand mooi op
    pretty_gpx = prettify_xml(gpx)

    # Zet de geformatteerde string om naar een BytesIO object
    gpx_output = BytesIO(pretty_gpx.encode('utf-8'))

    return send_file(gpx_output, as_attachment=True, download_name="converted_poi.gpx", mimetype="application/gpx+xml")

if __name__ == "__main__":
    app.run(debug=True)
