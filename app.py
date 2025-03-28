from flask import Flask, request, send_file
from flask_cors import CORS
import xml.etree.ElementTree as ET
import os
from xml.dom import minidom

app = Flask(__name__)
CORS(app)

@app.route('/api/convert', methods=['POST'])
def convert_pq_to_poi():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    tree = ET.parse(file)
    root = tree.getroot()
    
    namespace = {"gpx": "http://www.topografix.com/GPX/1/0"}  # Correcte namespace behouden
    waypoints = root.findall(".//gpx:wpt", namespace)
    
    if not waypoints:
        return "Geen waypoints gevonden in het GPX-bestand!", 400
    
    new_gpx = ET.Element("gpx", {
        "version": "1.1",
        "creator": "PQ2POI",
        "xmlns": "http://www.topografix.com/GPX/1/0"
    })
    
    for wpt in waypoints:
        new_wpt = ET.SubElement(new_gpx, "wpt", {
            "lat": wpt.get("lat"),
            "lon": wpt.get("lon")
        })
        
        # Combineer <name>, <desc>, <url> in de <name> tag met line breaks
        name = wpt.find("gpx:name", namespace).text if wpt.find("gpx:name", namespace) is not None else ""
        desc = wpt.find("gpx:desc", namespace).text if wpt.find("gpx:desc", namespace) is not None else ""
        url = wpt.find("gpx:url", namespace).text if wpt.find
