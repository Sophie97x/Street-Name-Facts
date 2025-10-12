"""
Street information database and utilities
Contains historical information about street names and their origins
"""

import json
import re
from datetime import datetime

# Sample street name database with historical information
STREET_DATABASE = {
    "broadway": {
        "origin": "Originally a Native American trail, Broadway gets its name from being one of the widest streets in colonial New York",
        "summary": "A wide thoroughfare originally based on Native American paths",
        "facts": [
            {"year": 1642, "fact": "Originally called 'Heere Straat' (Gentleman's Street) by Dutch colonists"},
            {"year": 1664, "fact": "Renamed 'Broadway' by English colonists due to its unusual width"},
            {"year": 1899, "fact": "Became famous as the theater district in New York City"},
            {"year": 1940, "fact": "Broadway theaters established as cultural landmarks"}
        ],
        "variations": ["broadway", "broad way", "broadway avenue", "broadway street"],
        "common_cities": ["New York", "San Francisco", "Los Angeles", "Chicago"]
    },
    "main street": {
        "origin": "Main Street typically refers to the primary commercial thoroughfare in American towns",
        "summary": "The central business district street in most American communities",
        "facts": [
            {"year": 1785, "fact": "First recorded use of 'Main Street' in American town planning"},
            {"year": 1920, "fact": "Sinclair Lewis novel 'Main Street' popularized the term"},
            {"year": 1950, "fact": "Main Street became symbol of small-town America"},
            {"year": 1980, "fact": "Main Street revitalization programs began nationwide"}
        ],
        "variations": ["main st", "main street", "main ave", "main avenue"],
        "common_cities": ["Most American towns and cities"]
    },
    "church street": {
        "origin": "Named after churches or religious institutions located on or near the street",
        "summary": "Streets named for their proximity to religious buildings",
        "facts": [
            {"year": 1630, "fact": "First Church Streets appeared in New England colonial settlements"},
            {"year": 1750, "fact": "Common naming pattern spread throughout American colonies"},
            {"year": 1800, "fact": "Church Street became one of the most common street names in America"},
            {"year": 1900, "fact": "Found in over 8,000 American communities"}
        ],
        "variations": ["church st", "church street", "church ave", "church avenue"],
        "common_cities": ["Boston", "Philadelphia", "Charleston", "Burlington"]
    },
    "oak street": {
        "origin": "Named after oak trees that were prominent along the street or in the area",
        "summary": "Tree-based street naming was popular in 19th century urban planning",
        "facts": [
            {"year": 1850, "fact": "Tree-named streets became popular during urban expansion"},
            {"year": 1880, "fact": "Oak Street became one of the most common tree-based street names"},
            {"year": 1920, "fact": "Many original oak trees removed for development"},
            {"year": 1970, "fact": "Urban forestry movements began replanting oak trees on Oak Streets"}
        ],
        "variations": ["oak st", "oak street", "oak ave", "oak avenue", "oakwood"],
        "common_cities": ["Chicago", "Detroit", "Minneapolis", "Portland"]
    },
    "first street": {
        "origin": "Numerical street naming system, typically the first street in a planned grid",
        "summary": "Part of systematic urban planning using numbers for organization",
        "facts": [
            {"year": 1811, "fact": "New York City's grid plan popularized numbered streets"},
            {"year": 1850, "fact": "Numbered street systems adopted by western American cities"},
            {"year": 1900, "fact": "First Street through Tenth Street became standard in many cities"},
            {"year": 1950, "fact": "Some cities renamed numbered streets for more character"}
        ],
        "variations": ["1st street", "first st", "1st st", "first avenue"],
        "common_cities": ["New York", "Philadelphia", "Seattle", "San Francisco"]
    },
    "wall street": {
        "origin": "Named after a wall built by Dutch colonists in 1653 to defend New Amsterdam",
        "summary": "Originally a defensive barrier, now synonymous with American finance",
        "facts": [
            {"year": 1653, "fact": "Dutch built wooden wall to defend against British and Native attacks"},
            {"year": 1699, "fact": "Wall demolished, but street name remained"},
            {"year": 1792, "fact": "Buttonwood Agreement signed, establishing New York Stock Exchange"},
            {"year": 1929, "fact": "Wall Street Crash marked beginning of Great Depression"},
            {"year": 1987, "fact": "Black Monday stock market crash occurred"},
            {"year": 2008, "fact": "Financial crisis centered on Wall Street institutions"}
        ],
        "variations": ["wall st", "wall street"],
        "common_cities": ["New York", "Various cities with Wall Street named after NYC"]
    },
    "high street": {
        "origin": "British term for the main street of a town, from Old English meaning 'important street'",
        "summary": "The primary commercial and social center of British towns",
        "facts": [
            {"year": 1200, "fact": "Term 'High Street' first recorded in medieval England"},
            {"year": 1500, "fact": "High Streets became centers of commerce and trade"},
            {"year": 1800, "fact": "High Street shopping became integral to British town life"},
            {"year": 1960, "fact": "Pedestrianization of High Streets began"},
            {"year": 2000, "fact": "Online shopping challenged traditional High Street retail"}
        ],
        "variations": ["high st", "high street", "the high street"],
        "common_cities": ["London", "Edinburgh", "Manchester", "Birmingham", "Oxford"]
    }
}

def normalize_street_name(street_name):
    """Normalize street name for database lookup"""
    # Convert to lowercase and remove common suffixes
    normalized = street_name.lower().strip()
    
    # Remove common street suffixes
    suffixes = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln', 'way', 'blvd', 'boulevard']
    
    for suffix in suffixes:
        if normalized.endswith(' ' + suffix):
            normalized = normalized[:-len(suffix)-1].strip()
        elif normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    
    return normalized

def get_street_info(street_name, city="", country=""):
    """Get information about a street name"""
    normalized_name = normalize_street_name(street_name)
    
    # Check if we have specific information about this street
    if normalized_name in STREET_DATABASE:
        info = STREET_DATABASE[normalized_name].copy()
        info['found'] = True
        info['search_term'] = street_name
        return info
    
    # Check variations
    for key, data in STREET_DATABASE.items():
        if 'variations' in data:
            for variation in data['variations']:
                if normalized_name == normalize_street_name(variation):
                    info = data.copy()
                    info['found'] = True
                    info['search_term'] = street_name
                    return info
    
    # Generate generic information based on street name patterns
    generic_info = generate_generic_info(street_name, city, country)
    return generic_info

def generate_generic_info(street_name, city="", country=""):
    """Generate generic information for streets not in our database"""
    normalized = normalize_street_name(street_name)
    
    # Pattern-based information
    patterns = {
        'tree_names': ['oak', 'maple', 'elm', 'pine', 'cedar', 'birch', 'willow', 'cherry'],
        'numbers': ['first', 'second', 'third', '1st', '2nd', '3rd'] + [str(i) for i in range(1, 21)],
        'presidents': ['washington', 'lincoln', 'jefferson', 'adams', 'madison', 'monroe'],
        'directions': ['north', 'south', 'east', 'west', 'central'],
        'features': ['hill', 'valley', 'ridge', 'creek', 'river', 'lake', 'park']
    }
    
    info = {
        'found': False,
        'search_term': street_name,
        'origin': f"Information about {street_name} is not available in our database.",
        'summary': f"Street name: {street_name}",
        'facts': [],
        'variations': [street_name.lower()],
        'common_cities': []
    }
    
    # Check for patterns and provide relevant information
    for tree in patterns['tree_names']:
        if tree in normalized:
            info['origin'] = f"Likely named after {tree} trees that were prominent in the area when the street was established."
            info['summary'] = f"A tree-named street, part of nature-inspired urban planning"
            info['facts'] = [
                {"year": 1850, "fact": f"Tree-named streets like {tree.title()} became popular during 19th century urban development"},
                {"year": 1900, "fact": f"Many {tree} trees may have been planted along this street"},
                {"year": 1950, "fact": f"Urban development may have removed original {tree} trees"}
            ]
            break
    
    for num in patterns['numbers']:
        if num in normalized or normalized.startswith(num):
            info['origin'] = f"Part of a numbered street system used for organized urban planning."
            info['summary'] = f"Systematically numbered street for easy navigation"
            info['facts'] = [
                {"year": 1811, "fact": "Numbered street systems popularized by New York City's grid plan"},
                {"year": 1850, "fact": "Many American cities adopted numbered street naming"},
                {"year": 1900, "fact": "Numbered streets became standard in urban planning"}
            ]
            break
    
    for president in patterns['presidents']:
        if president in normalized:
            info['origin'] = f"Named in honor of President {president.title()}, reflecting American patriotic street naming traditions."
            info['summary'] = f"Presidential street name honoring {president.title()}"
            info['facts'] = [
                {"year": 1800, "fact": f"Streets began being named after President {president.title()}"},
                {"year": 1850, "fact": "Presidential street names became common across America"},
                {"year": 1900, "fact": f"{president.title()} Street found in hundreds of American cities"}
            ]
            break
    
    return info

def search_streets_by_name(query, limit=10):
    """Search for streets matching a query"""
    query_lower = query.lower()
    results = []
    
    # Search in our database
    for street_name, data in STREET_DATABASE.items():
        if query_lower in street_name or street_name.startswith(query_lower):
            results.append({
                'name': street_name.title(),
                'summary': data['summary'],
                'origin': data['origin'][:100] + "..." if len(data['origin']) > 100 else data['origin']
            })
        
        # Check variations
        if 'variations' in data:
            for variation in data['variations']:
                if query_lower in variation and street_name.title() not in [r['name'] for r in results]:
                    results.append({
                        'name': variation.title(),
                        'summary': data['summary'],
                        'origin': data['origin'][:100] + "..." if len(data['origin']) > 100 else data['origin']
                    })
    
    return results[:limit]

def get_random_street_fact():
    """Get a random interesting street fact"""
    import random
    
    all_facts = []
    for street_data in STREET_DATABASE.values():
        if 'facts' in street_data:
            all_facts.extend(street_data['facts'])
    
    if all_facts:
        return random.choice(all_facts)
    return {"year": 2024, "fact": "Street names tell the story of our communities and history."}