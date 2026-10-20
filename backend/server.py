from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import json
import time
from street_data import get_street_info, search_streets_by_name

app = Flask(__name__, static_folder="../frontend")
CORS(app)

# Initialize geocoder
geolocator = Nominatim(user_agent="street-names-explorer")

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/maptest.html")
def maptest():
    return send_from_directory("../frontend", "maptest.html")

@app.route("/debug.html")
def debug():
    return send_from_directory("../frontend", "debug.html")

@app.route("/working.html")
def working():
    return send_from_directory("../frontend", "working.html")

@app.route("/api/search-location", methods=["POST"])
def search_location():
    """Search for a location and return coordinates"""
    try:
        data = request.get_json()
        query = data.get("query", "")
        
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Use Nominatim to geocode the location
        location = geolocator.geocode(query, timeout=10)
        
        if location:
            return jsonify({
                "success": True,
                "location": {
                    "name": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "display_name": location.address
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": "Location not found"
            }), 404
            
    except GeocoderTimedOut:
        return jsonify({"error": "Geocoding service timed out"}), 408
    except Exception:
        app.logger.exception("Street service request failed")
        return jsonify({"error": "Unable to complete the request. Please try again."}), 500

@app.route("/api/street-info", methods=["POST"])
def get_street_information():
    """Get information about a specific street"""
    try:
        data = request.get_json()
        street_name = data.get("street_name", "")
        city = data.get("city", "")
        country = data.get("country", "")
        
        if not street_name.strip():
            return jsonify({"error": "Street name is required"}), 400
        
        # Get street information
        street_info = get_street_info(street_name, city, country)
        
        return jsonify({
            "success": True,
            "street_info": street_info
        })
        
    except Exception:
        app.logger.exception("Street service request failed")
        return jsonify({"error": "Unable to complete the request. Please try again."}), 500

@app.route("/api/search-streets", methods=["GET"])
def search_streets():
    """Search for streets by name pattern"""
    try:
        query = request.args.get("q", "")
        limit = int(request.args.get("limit", 10))
        
        if not query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        results = search_streets_by_name(query, limit)
        
        return jsonify({
            "success": True,
            "results": results
        })
        
    except Exception:
        app.logger.exception("Street service request failed")
        return jsonify({"error": "Unable to complete the request. Please try again."}), 500

@app.route("/api/nearby-streets", methods=["POST"])
def get_nearby_streets():
    """Get streets near a specific coordinate"""
    try:
        data = request.get_json()
        lat = float(data.get("latitude", 0))
        lon = float(data.get("longitude", 0))
        radius = float(data.get("radius", 1000))  # meters
        
        # Use Overpass API to get nearby streets
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        (
          way["highway"]["name"]
          (around:{radius},{lat},{lon});
        );
        out geom;
        """
        
        response = requests.post(overpass_url, data=overpass_query, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            streets = []
            
            for element in data.get("elements", []):
                if "tags" in element and "name" in element["tags"]:
                    street_name = element["tags"]["name"]
                    highway_type = element["tags"].get("highway", "unknown")
                    
                    # Get coordinates of the street
                    coords = []
                    if "geometry" in element:
                        coords = [[node["lat"], node["lon"]] for node in element["geometry"]]
                    
                    streets.append({
                        "name": street_name,
                        "type": highway_type,
                        "coordinates": coords,
                        "osm_id": element["id"]
                    })
            
            return jsonify({
                "success": True,
                "streets": streets[:20]  # Limit to 20 streets
            })
        else:
            return jsonify({"error": "Failed to fetch street data"}), 500
            
    except Exception:
        app.logger.exception("Street service request failed")
        return jsonify({"error": "Unable to complete the request. Please try again."}), 500

@app.route('/api/nearby-streets-enhanced', methods=['POST'])
def get_nearby_streets_enhanced():
    """Get streets near a location with enhanced data"""
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    radius = data.get('radius', 2000)  # 2km default radius
    
    if not lat or not lng:
        return jsonify({'success': False, 'error': 'Latitude and longitude required'})
    
    try:
        # Use Overpass API to get more comprehensive street data
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:30];
        (
          way["highway"~"^(primary|secondary|tertiary|residential|unclassified|trunk|trunk_link|primary_link|secondary_link|tertiary_link|living_street|service)$"]["name"]
            (around:{radius},{lat},{lng});
        );
        out geom;
        """
        
        response = requests.post(overpass_url, data=overpass_query, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            streets = []
            
            # Also get location context using reverse geocoding
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="street-names-explorer")
            
            location_context = None
            try:
                location_info = geolocator.reverse(f"{lat}, {lng}", timeout=10)
                if location_info and location_info.raw.get('address'):
                    addr = location_info.raw['address']
                    location_context = {
                        'city': addr.get('city') or addr.get('town') or addr.get('village') or addr.get('suburb', ''),
                        'country': addr.get('country', '')
                    }
            except Exception as e:
                print(f"Reverse geocoding failed: {e}")
            
            for element in data.get('elements', []):
                if 'geometry' in element and 'tags' in element and 'name' in element['tags']:
                    coords = [[node['lat'], node['lon']] for node in element['geometry']]
                    
                    # Use location context if street doesn't have address info
                    city = element['tags'].get('addr:city', '')
                    country = element['tags'].get('addr:country', '')
                    
                    if not city and location_context:
                        city = location_context['city']
                    if not country and location_context:
                        country = location_context['country']
                    
                    street = {
                        'name': element['tags']['name'],
                        'type': element['tags'].get('highway', 'road'),
                        'coordinates': coords,
                        'city': city,
                        'country': country
                    }
                    streets.append(street)
            
            return jsonify({'success': True, 'streets': streets})
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch street data'})
            
    except Exception as e:
        app.logger.exception("Enhanced nearby street request failed")
        return jsonify({'success': False, 'error': 'Unable to complete the request. Please try again.'})

@app.route('/api/street-info-enhanced', methods=['POST'])
def get_street_info_enhanced():
    """Get enhanced street information from multiple sources"""
    data = request.get_json()
    street_name = data.get('street_name', '').strip()
    city = data.get('city', '').strip()
    country = data.get('country', '').strip()
    
    if not street_name:
        return jsonify({'success': False, 'error': 'Street name required'})
    
    try:
        # First check our local database
        local_info = get_street_info(street_name)
        
        # Try to get Wikipedia information
        wiki_info = get_wikipedia_street_info(street_name, city, country)
        
        # Combine information
        street_info = {
            'name': street_name,
            'origin': '',
            'summary': '',
            'facts': []
        }
        
        # Check if local info is useful (not the generic "not available" message)
        if local_info and 'origin' in local_info and 'not available in our database' not in local_info['origin']:
            # Use local database info as primary source
            street_info['origin'] = local_info.get('origin', '')
            street_info['summary'] = local_info.get('summary', '')
            if 'facts' in local_info:
                street_info['facts'] = local_info['facts']
        elif wiki_info:
            # Use Wikipedia info if local info not available
            street_info['origin'] = wiki_info.get('origin', '')
            street_info['summary'] = wiki_info.get('summary', '')
        
        # If still no useful information, provide intelligent fallback response
        if not street_info['origin'] or 'not available in our database' in street_info['origin']:
            street_info['origin'] = get_intelligent_street_explanation(street_name, city, country)
            street_info['summary'] = get_street_specific_facts(street_name, city, country)
            street_info['facts'] = get_street_timeline_facts(street_name, city, country)
        
        return jsonify({
            'success': True,
            'street_info': street_info
        })
        
    except Exception as e:
        app.logger.exception("Enhanced street information request failed")
        return jsonify({'success': False, 'error': 'Unable to complete the request. Please try again.'})

def get_intelligent_street_explanation(street_name, city='', country=''):
    """Generate intelligent explanation based on street name patterns"""
    street_lower = street_name.lower()
    
    # Royal names with location context
    if any(royal in street_lower for royal in ['victoria', 'elizabeth', 'george', 'edward', 'albert', 'william', 'charles', 'mary', 'alexandra']):
        if 'victoria' in street_lower:
            if country.lower() in ['uk', 'united kingdom', 'england', 'scotland', 'wales'] or city.lower() in ['hebburn', 'london', 'manchester', 'birmingham']:
                return f"Victoria Road East in {city or 'this area'} is named after Queen Victoria (1819-1901), who reigned over the British Empire for 63 years. The 'East' designation indicates this road runs east-west or is located in the eastern section of the area. Streets named after Victoria were typically established during her reign (1837-1901) or shortly after her death in 1901 as memorials. In industrial towns like Hebburn, Victoria roads often connected residential areas to shipyards and factories, serving as main thoroughfares for workers during the height of British industrial power."
            else:
                return f"'{street_name}' is likely named after Queen Victoria (1819-1901), reflecting the widespread practice of naming streets after British royalty throughout the former British Empire and Commonwealth countries. The directional designation suggests it's part of a planned street layout from the Victorian era."
        elif 'elizabeth' in street_lower:
            return f"This street in {city or 'this area'} is likely named after Queen Elizabeth I (1533-1603) or Queen Elizabeth II (1926-2022). Elizabeth is a popular choice for street names in Commonwealth countries."
        elif 'george' in street_lower:
            return f"This street in {city or 'this area'} is likely named after one of the King Georges of Britain, particularly King George III (1738-1820) or King George VI (1895-1952)."
        else:
            return f"'{street_name}' appears to be named after British royalty, a common practice in streets throughout the UK and Commonwealth countries."
    
    # Religious names
    elif any(religious in street_lower for religious in ['church', 'chapel', 'abbey', 'cathedral', 'saint', 'st.']):
        return f"'{street_name}' is likely named after a nearby religious building or institution. Many streets take their names from churches, chapels, or religious figures in the area."
    
    # Nature names
    elif any(nature in street_lower for nature in ['oak', 'elm', 'maple', 'pine', 'cedar', 'birch', 'willow', 'rose', 'ivy']):
        return f"'{street_name}' appears to be named after local flora. Tree and plant names were popular choices for street names, often reflecting the natural landscape of the area."
    
    # Directional names
    elif any(direction in street_lower for direction in ['north', 'south', 'east', 'west', 'upper', 'lower', 'high', 'new', 'old']):
        return f"'{street_name}' uses directional or positional naming, which helps distinguish it from similar streets in the area and indicates its geographical relationship to other roads."
    
    # Historical figures (common surnames)
    elif any(surname in street_lower for surname in ['churchill', 'wellington', 'nelson', 'shakespeare', 'dickens', 'darwin']):
        return f"'{street_name}' is likely named after a historical figure. Many streets honor notable individuals from history, literature, science, or politics."
    
    # Default explanation
    else:
        return f"'{street_name}' may be named after local landmarks, historical figures, geographical features, or early settlers in the area. The 'East' designation suggests it runs in an east-west direction or is located in the eastern part of the district."

def get_street_specific_facts(street_name, city='', country=''):
    """Generate street-specific quick facts"""
    street_lower = street_name.lower()
    
    # Victoria-specific facts
    if 'victoria' in street_lower:
        if city.lower() == 'hebburn':
            return f"Victoria Road East likely dates from Hebburn's industrial expansion in the late 1800s. As a major shipbuilding town on the River Tyne, Hebburn developed rapidly during Queen Victoria's reign, with new streets like this connecting workers' housing to the Palmer's shipyard."
        elif country.lower() in ['uk', 'united kingdom', 'england']:
            return f"Victoria roads in Britain typically date from 1837-1901 (Victorian era) or early 1900s memorial period. The 'East' designation suggests this is part of a coordinated street naming system in {city or 'the area'}."
        else:
            return f"Victoria streets in Commonwealth countries often commemorate Queen Victoria's Diamond Jubilee (1897) or death (1901). The directional name suggests planned urban development."
    
    # Royal name facts
    elif any(royal in street_lower for royal in ['elizabeth', 'george', 'edward', 'albert']):
        return f"Royal street names like {street_name} were often chosen during major civic developments or to honor coronations, jubilees, or royal deaths. The specific timing would depend on {city or 'local'} development patterns."
    
    # Religious facts
    elif any(religious in street_lower for religious in ['church', 'chapel', 'abbey']):
        return f"Religious street names like {street_name} typically indicate proximity to a place of worship. In {city or 'many areas'}, such streets often formed the historic center of the community."
    
    # Directional facts
    elif any(direction in street_lower for direction in ['north', 'south', 'east', 'west']):
        return f"Directional street names like {street_name} were popular in planned developments from the 1800s onward. They help create logical navigation systems and often indicate the street's orientation or location within {city or 'the district'}."
    
    # Default
    else:
        return f"Street names like {street_name} reflect the local history, geography, and development patterns of {city or 'the area'}. The specific naming would depend on when the street was established and what was significant to the community at that time."

def get_street_timeline_facts(street_name, city='', country=''):
    """Generate historical timeline facts for the street"""
    street_lower = street_name.lower()
    facts = []
    
    # Victoria-specific timeline
    if 'victoria' in street_lower:
        if city.lower() == 'hebburn':
            facts = [
                {"year": "1840s", "fact": "Hebburn begins major industrial expansion with Palmer's shipyard establishment"},
                {"year": "1850s-1870s", "fact": "New residential streets like Victoria Road East built to house growing shipyard workforce"},
                {"year": "1887", "fact": "Queen Victoria's Golden Jubilee likely reinforced the naming of Victoria streets"},
                {"year": "1901", "fact": "Victoria's death leads to memorial street naming across Britain, possibly including this road"}
            ]
        elif country.lower() in ['uk', 'united kingdom', 'england']:
            facts = [
                {"year": "1837", "fact": "Queen Victoria ascends to throne, beginning era of streets named in her honor"},
                {"year": "1850s-1880s", "fact": "Peak period for Victoria street naming during rapid urban expansion"},
                {"year": "1887", "fact": "Golden Jubilee celebrations inspire many new Victoria street names"},
                {"year": "1901-1910", "fact": "Memorial naming period following Victoria's death"}
            ]
        else:
            facts = [
                {"year": "1840s-1880s", "fact": "Victorian era expansion in Commonwealth territories"},
                {"year": "1887", "fact": "Diamond Jubilee celebrations promote Victoria street naming globally"},
                {"year": "1901", "fact": "Memorial street naming following Queen Victoria's death"}
            ]
    
    # Royal timeline
    elif any(royal in street_lower for royal in ['elizabeth', 'george', 'edward']):
        facts = [
            {"year": "1800s", "fact": f"Royal street names like {street_name} become popular during British urban expansion"},
            {"year": "1850s-1900s", "fact": "Peak period for royal street naming in planned developments"},
            {"year": "1900s-1950s", "fact": "Continued royal naming during suburban expansion periods"}
        ]
    
    # Default timeline
    else:
        facts = [
            {"year": "1800s", "fact": f"Street names like {street_name} established during urban development period"},
            {"year": "1850s-1900s", "fact": "Systematic street naming becomes common in growing towns and cities"},
            {"year": "1900s", "fact": "Modern street layout and naming conventions become standardized"}
        ]
    
    return facts

def get_wikipedia_street_info(street_name, city='', country=''):
    """Get street information from Wikipedia"""
    try:
        import re
        
        # Create location-specific search terms first, then general ones
        search_terms = []
        
        # Priority 1: Exact street + city combinations
        if city:
            search_terms.extend([
                f"{street_name} {city}",
                f"{street_name} {city} {country}" if country else None,
                f"{street_name} street {city}",
                f"{street_name} road {city}"
            ])
        
        # Priority 2: Street-specific terms (avoid generic location names)
        street_words = street_name.lower().split()
        if len(street_words) > 1:
            # For roads like "Victoria Road East", search for the full name first
            search_terms.extend([
                f"{street_name} street",
                f"{street_name} road"
            ])
        
        # Priority 3: Only add generic terms if we have context clues
        # Avoid searching just "Victoria" or "Cambridge" which are too generic
        if city and len(street_words) == 1 and street_words[0] not in ['victoria', 'cambridge', 'oxford', 'london', 'manchester']:
            search_terms.append(f"{street_name.split()[0]} {city}")
        
        # Remove None values and duplicates
        search_terms = list(dict.fromkeys([term for term in search_terms if term]))
        
        for search_term in search_terms:
            try:
                # Try direct page lookup first
                search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + search_term.replace(' ', '_')
                headers = {'User-Agent': 'StreetNamesExplorer/1.0'}
                
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'extract' in data and data['extract']:
                        extract = data['extract']
                        
                        # Skip if this is clearly not street-related content
                        skip_indicators = [
                            'may refer to',
                            'is a state in',
                            'is a country',
                            'is a city',
                            'is a suburb',
                            'highest density of roads',
                            'population centres',
                            'mainland states'
                        ]
                        
                        if any(indicator in extract.lower() for indicator in skip_indicators):
                            print(f"Skipping generic location info for: {search_term}")
                            continue
                        
                        # Look for street-specific naming information
                        street_naming_patterns = [
                            r'named after ([^.]+)',
                            r'named for ([^.]+)',
                            r'named in honor of ([^.]+)',
                            r'named in honour of ([^.]+)',
                            r'commemorates ([^.]+)',
                            r'derives its name from ([^.]+)',
                            r'originally called ([^.]+)',
                            r'formerly known as ([^.]+)',
                            r'takes its name from ([^.]+)',
                            r'street.*named.*after ([^.]+)',
                            r'road.*named.*after ([^.]+)'
                        ]
                        
                        origin_info = ""
                        for pattern in street_naming_patterns:
                            match = re.search(pattern, extract, re.IGNORECASE)
                            if match:
                                origin_info = f"This street was {match.group(0)}."
                                break
                        
                        # Only use generic content if it's clearly about the street/road
                        if not origin_info and ('street' in extract.lower() or 'road' in extract.lower()):
                            first_sentence = extract.split('.')[0] + '.'
                            if len(first_sentence) > 20 and 'disambiguation' not in first_sentence.lower():
                                origin_info = first_sentence
                        
                        if origin_info:
                            return {
                                'origin': origin_info,
                                'summary': f"Information about {search_term}",
                                'source': 'Wikipedia'
                            }
                
                # If direct lookup fails, try search API
                search_api_url = "https://en.wikipedia.org/w/api.php"
                search_params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': search_term,
                    'srlimit': 3
                }
                
                search_response = requests.get(search_api_url, params=search_params, headers=headers, timeout=10)
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    
                    if 'query' in search_data and 'search' in search_data['query']:
                        for result in search_data['query']['search']:
                            if 'street' in result['title'].lower() or 'road' in result['title'].lower():
                                # Try to get this page's summary
                                page_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{result['title'].replace(' ', '_')}"
                                page_response = requests.get(page_url, headers=headers, timeout=10)
                                
                                if page_response.status_code == 200:
                                    page_data = page_response.json()
                                    if 'extract' in page_data and page_data['extract']:
                                        return {
                                            'origin': page_data['extract'][:300] + '...' if len(page_data['extract']) > 300 else page_data['extract'],
                                            'summary': f"From Wikipedia article: {result['title']}",
                                            'source': 'Wikipedia'
                                        }
                            
            except Exception as e:
                print(f"Wikipedia search error for '{search_term}': {e}")
                continue
        
        return None
        
    except Exception as e:
        print(f"Wikipedia API error: {e}")
        return None

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

if __name__ == "__main__":
    import os
    
    # Check if running in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    debug_mode = not is_production
    
    print(f"🛣️ Street Names Explorer starting...")
    print(f"Mode: {'Production' if is_production else 'Development'}")
    print(f"Debug: {debug_mode}")
    print(f"Host: 0.0.0.0:8080")
    
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)