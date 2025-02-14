import subprocess
import re
import requests
import json
from typing import List, Dict
from datetime import datetime

def get_traceroute(target: str) -> List[str]:
    """
    Executes traceroute and returns a list of IPs.
    """
    if subprocess.os.name == 'nt':  # Windows
        command = ['tracert', target]
    else:  # Unix/Linux/MacOS
        command = ['traceroute', target]
        
    try:
        output = subprocess.check_output(command, text=True)
        # Extract IPs using regular expression
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        ips = re.findall(ip_pattern, output)
        
        new_ips = ips[2:]  # Remove first two IPs 
        
        # Find my public IP and add it to the list in the first position
        my_ip = requests.get('https://api64.ipify.org').text
        new_ips.insert(0, my_ip)
        
        return new_ips
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing traceroute: {e}")
        return []

def get_ip_location(ip: str) -> Dict[str, str]:
    """
    Gets the location of an IP using the ip-api.com API.
    """
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        data = response.json()
        if data['status'] == 'success':
            return {
                'country': data['country'],
                'city': data['city'],
                'lat': data['lat'],
                'lon': data['lon'],
                'isp': data['isp']
            }
        return {
            'country': 'Unknown',
            'city': 'Unknown',
            'lat': 0,
            'lon': 0,
            'isp': 'Unknown'
        }
    except Exception as e:
        print(f"Error getting location for IP {ip}: {e}")
        return {
            'country': 'Unknown',
            'city': 'Unknown',
            'lat': 0,
            'lon': 0,
            'isp': 'Unknown'
        }

def save_route_data(ips: List[str], locations: List[Dict]) -> None:
    """
    Saves the route data to a JSON file.
    """
    route_data = {
        'timestamp': datetime.now().isoformat(),
        'hops': []
    }
    
    for i, (ip, location) in enumerate(zip(ips, locations)):
        hop_data = {
            'hop_number': i + 1,
            'ip': ip,
            'location': location
        }
        route_data['hops'].append(hop_data)
    
    filename = f'route_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(route_data, f, indent=2, ensure_ascii=False)
    
    print(f"Route data saved in {filename}")

def create_map_visualization(ips: List[str], locations: List[Dict]) -> None:
    """
    Creates an HTML file with a world map showing the network path.
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Network Path Visualization</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.css" />
        <style>
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
            }
            #map {
                height: 100%;
                width: 100%;
            }
            .legend {
                padding: 10px;
                background: white;
                background: rgba(255,255,255,0.9);
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                border-radius: 5px;
                line-height: 24px;
            }
            .legend i {
                width: 18px;
                height: 18px;
                float: left;
                margin-right: 8px;
                opacity: 0.7;
                border-radius: 50%;
            }
            .arrow-legend {
                width: 30px;
                height: 2px;
                background: red;
                display: inline-block;
                margin: 0 8px;
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js"></script>
        <script>
            const points = POINTS_DATA;
            
            // Find the bounds of all valid points
            const validPoints = points.filter(p => p.lat !== 0 && p.lon !== 0);
            const lats = validPoints.map(p => p.lat);
            const lons = validPoints.map(p => p.lon);
            const minLat = Math.min(...lats);
            const maxLat = Math.max(...lats);
            const minLon = Math.min(...lons);
            const maxLon = Math.max(...lons);
            
            // Calculate center and bounds with padding
            const centerLat = (minLat + maxLat) / 2;
            const centerLon = (minLon + maxLon) / 2;
            
            // Initialize map with calculated center
            const map = L.map('map').setView([centerLat, centerLon], 2);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            let lastValidPoint = null;
            const validLocations = [];
            
            // Create markers and store valid locations
            points.forEach((point, index) => {
                if (point.lat !== 0 || point.lon !== 0) {
                    const color = index === 0 ? '#00ff00' : 
                                index === points.length - 1 ? '#0000ff' : '#ff0000';
                    
                    const marker = L.circleMarker([point.lat, point.lon], {
                        radius: 8,
                        fillColor: color,
                        color: '#fff',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(map);
                    
                    marker.bindPopup(
                        `<b>Hop ${index + 1}</b><br>` +
                        `IP: ${point.ip}<br>` +
                        `Location: ${point.city}, ${point.country}<br>` +
                        `ISP: ${point.isp}`
                    );
                    
                    validLocations.push({
                        point: point,
                        index: index
                    });
                }
            });
            
            // Draw arrows between consecutive valid points
            for (let i = 0; i < validLocations.length - 1; i++) {
                const currentPoint = validLocations[i].point;
                const nextPoint = validLocations[i + 1].point;
                
                // Create arrow line
                const latlngs = [[currentPoint.lat, currentPoint.lon], [nextPoint.lat, nextPoint.lon]];
                const arrow = L.polyline(latlngs, {
                    color: 'red',
                    weight: 2,
                    opacity: 0.8,
                    dashArray: '10, 10'
                }).addTo(map);
                
                // Add arrowhead at midpoint
                const midLat = (currentPoint.lat + nextPoint.lat) / 2;
                const midLon = (currentPoint.lon + nextPoint.lon) / 2;
                
                // Calculate angle for arrowhead
                const angle = Math.atan2(nextPoint.lat - currentPoint.lat, nextPoint.lon - currentPoint.lon);
                const arrowLength = 1;  // Increased arrow size
                const arrowAngle = Math.PI / 6;
                
                const p1 = [
                    midLat - arrowLength * Math.sin(angle - arrowAngle),
                    midLon - arrowLength * Math.cos(angle - arrowAngle)
                ];
                const p2 = [
                    midLat - arrowLength * Math.sin(angle + arrowAngle),
                    midLon - arrowLength * Math.cos(angle + arrowAngle)
                ];
                
                L.polyline([[p1[0], p1[1]], [midLat, midLon], [p2[0], p2[1]]], {
                    color: 'red',
                    weight: 2,
                    opacity: 0.8
                }).addTo(map);
            }
            
            // Fit bounds with padding
            const bounds = L.latLngBounds([minLat, minLon], [maxLat, maxLon]);
            map.fitBounds(bounds, {
                padding: [50, 50],
                maxZoom: 4
            });

            // Add legend
            const legend = L.control({position: 'bottomright'});
            legend.onAdd = function (map) {
                const div = L.DomUtil.create('div', 'legend');
                div.innerHTML = `
                    <h4>Network Path Legend</h4>
                    <i style="background: #00ff00"></i> Origin Point<br>
                    <i style="background: #ff0000"></i> Intermediate Hop<br>
                    <i style="background: #0000ff"></i> Destination<br>
                    <div style="margin-top: 10px;">
                        <span class="arrow-legend"></span> Network Path
                    </div>
                `;
                return div;
            };
            legend.addTo(map);
        </script>
    </body>
    </html>
    """
    
    # Prepare points data
    points_data = []
    for i, (ip, location) in enumerate(zip(ips, locations)):
        points_data.append({
            'ip': ip,
            'lat': location['lat'],
            'lon': location['lon'],
            'city': location['city'],
            'country': location['country'],
            'isp': location['isp']
        })
    
    # Replace placeholder in template
    html_content = html_template.replace('POINTS_DATA', json.dumps(points_data))
    
    # Save to file
    filename = 'network_path.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Map visualization saved as '{filename}'")

def main():
    target = input("Enter the target domain or IP: ")
    print(f"Executing traceroute to {target}...")
    
    ips = get_traceroute(target)
    if ips:
        print("Getting geolocation information...")
        locations = [get_ip_location(ip) for ip in ips]
        
        print("Creating map visualization...")
        create_map_visualization(ips, locations)
        print("Visualization saved as 'network_path.html'")
        
        print("Saving route data...")
        save_route_data(ips, locations)
    else:
        print("Could not get network hops.")

if __name__ == "__main__":
    main()
