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
        url = wpt.find("gpx:url", namespace).text if wpt.find("gpx:url", namespace) is not None else ""
        
        # Maak de <name> tag op zoals gewenst
        combined_name = f"{name}\n{desc}\n{url}"
        
        # Voeg de gecombineerde naam toe aan de nieuwe <name> tag
        sub_name = ET.SubElement(new_wpt, "name")
        sub_name.text = combined_name
        
        # Voeg de andere sub-elementen toe aan het waypoint
        for child in wpt:
            sub_element = ET.SubElement(new_wpt, child.tag, child.attrib)
            sub_element.text = child.text
    
    gpx_data = ET.tostring(new_gpx, encoding='utf-8')
    formatted_gpx = minidom.parseString(gpx_data).toprettyxml(indent="  ")  # Mooie opmaak
    
    output_file = "converted_poi.gpx"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted_gpx)
    
    return send_file(output_file, as_attachment=True, download_name="converted_poi.gpx", mimetype="application/gpx+xml")

if __name__ == '__main__':
    app.run(debug=True)
