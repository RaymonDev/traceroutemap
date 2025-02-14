# Network Traceroute Visualization

A Python tool that creates an interactive visualization of network paths using traceroute data. This tool maps out the physical journey of your network requests, showing the geographic location of each hop from source to destination.

## Features

- Performs traceroute to any specified domain or IP address
- Retrieves geolocation data for each network hop
- Creates an interactive web-based visualization using Leaflet.js
- Saves detailed route data in JSON format
- Supports both Windows and Unix-based systems

## Requirements

- Python 3.6+
- Internet connection
- ```traceroute``` (Unix/Linux/MacOS) or ```tracert``` (Windows) utility installed

## Installation

1. Clone this repository

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python network_path.py
```

2. Enter the target domain or IP address when prompted.

3. The script will generate two files:
   - `network_path.html`: Interactive map visualization
   - `route_data_YYYYMMDD_HHMMSS.json`: Detailed route data with timestamps

4. Open the HTML file in a web browser to view the visualization.



## API Rate Limits

This tool uses two external APIs:

1. ```ip-api.com``` (Geolocation API):
   - Free tier limitations:
     - 45 requests per minute
     - No API key required
     - Limited to non-commercial use

2. ```ipify.org``` (IP Detection API):
   - Free tier:
     - 1,000 requests per month
     - No API key required

Please note that exceeding these rate limits may result in temporary IP blocks.

## Output Examples

### Visualization
The generated HTML file creates an interactive map showing:
- Green marker: Starting point (your location)
- Red markers: Intermediate hops
- Blue marker: Destination
- Dashed red lines with arrows: Network path

### JSON Data Structure
```json
{
  "timestamp": "2025-02-13T10:30:45.123456",
  "hops": [
    {
      "hop_number": 1,
      "ip": "203.0.113.1",
      "location": {
        "country": "United States",
        "city": "New York",
        "lat": 40.7128,
        "lon": -74.0060,
        "isp": "Example ISP"
      }
    }
  ]
}
```

## Known Limitations

- Some network hops may not reveal their IP addresses (shown as * in traceroute)
- Geolocation data may not be 100% accurate
- Some IP addresses might be internal and won't have geolocation data
- The visualization may not work properly if too many hops are unresolved
- Only tested in Windows 11

## Possible errors and solutions

- If you get an error like `ModuleNotFoundError: No module named 'win32api'`, you need to install the `pywin32` package. You can install it by running the following command:
```bash
pip install pywin32
```

- If any kind of auth error happens and you are in Windows 11, please make sure you have your location turned on. You can do this by going to `Settings > Privacy & Security > Location` and turning on the location.



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- ```OpenStreetMap``` for map data
- ```Leaflet.js``` for map visualization
- ```ip-api.com``` for geolocation data
- ```ipify.org``` for public IP detection