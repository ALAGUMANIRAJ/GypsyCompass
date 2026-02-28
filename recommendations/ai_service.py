"""
GypsyCompass AI Service
=======================
Uses the NEW google-genai v1.x SDK (not the deprecated google-generativeai).
Reads GEMINI_API_KEY directly from os.environ / .env on every request,
so no server restart is needed after adding the key.

To enable AI: put your real key in .env:
    GEMINI_API_KEY=AIzaSy...
Get a free key at: https://aistudio.google.com/app/apikey
"""

import os
import json
import re
import random
import traceback
import sys
from dotenv import load_dotenv
from google.genai import types

# ── Ensure console output handles Unicode (Crucial for ₹ symbol on Windows) ──
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ── Load .env on every import so key changes reflect instantly ──
load_dotenv(override=True)


def _read_api_key():
    """Read the Gemini API key fresh from environment each time."""
    key = os.environ.get('GEMINI_API_KEY', '').strip()
    if key and key not in ('your_gemini_api_key_here', 'YOUR_KEY_HERE', ''):
        return key
    return None


def _build_genai_client(api_key):
    """Build a google-genai Client using the new v1.x SDK."""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        print(f"[AI] Failed to create genai client: {e}")
        return None


# ─────────────────────────────────────────────────────────
#  CURRENCY CONVERSIONS  (INR base — fallback database is in INR)
# ─────────────────────────────────────────────────────────
CURRENCY_TO_INR = {
    'INR': 1,
    'USD': 84,
    'EUR': 91,
    'GBP': 107,
    'AED': 23,
    'SGD': 63,
    'THB': 2.4,
    'MYR': 19,
}

# ─────────────────────────────────────────────────────────
#  STYLE ALIASES: Frontend label → backend destination tags
#  This bridges the gap between TripPlannerPage style names
#  and the tags used in ALL_DESTINATIONS.
# ─────────────────────────────────────────────────────────
STYLE_ALIASES = {
    # Frontend name (lowercased)       → list of backend tags that match
    'hill stations':                    ['hill stations'],
    'mountains':                        ['mountains', 'snow'],
    'forests & wildlife':               ['forests & wildlife'],
    'waterfalls':                       ['waterfalls', 'nature & landscape'],
    'beaches':                          ['beaches'],
    'backwaters & lakes':               ['backwaters & lakes', 'water-based'],
    'islands':                          ['islands'],
    'heritage sites':                   ['heritage sites', 'culture & heritage'],
    'temples & spiritual':              ['temples & spiritual'],
    'museums & arts':                   ['museums & arts', 'culture & heritage'],
    'deserts':                          ['deserts'],
    'caves':                            ['caves'],
    'adventure':                        ['adventure'],
    'city life':                        ['city life'],
    'village/rural tourism':            ['village/rural tourism'],
    # Also handle backend tags directly (for self-match)
    'culture & heritage':               ['culture & heritage', 'heritage sites'],
    'water-based':                      ['water-based', 'backwaters & lakes'],
    'nature & landscape':               ['nature & landscape', 'waterfalls'],
    'snow':                             ['snow', 'mountains'],
    'food & culinary':                  ['food & culinary'],
}

def _normalize_style(style: str) -> set:
    """Convert a user-selected style to a set of backend tags it should match."""
    s = style.lower().strip()
    if s in STYLE_ALIASES:
        return set(STYLE_ALIASES[s])
    # Fallback: return self + try word-level matching
    return {s}


# ─────────────────────────────────────────────────────────
#  FULL DESTINATION DATABASE  (fallback when AI unavailable)
# ─────────────────────────────────────────────────────────
ALL_DESTINATIONS = [
    # BEACH / COASTAL
    {
        "name": "Goa", "location": "Goa, India",
        "tagline": "Sun, sand & sea — India's beach capital",
        "styles": ["beaches", "water-based", "city life", "adventure", "food & culinary", "waterfalls"],
        "base_cost": 10000, "cost_per_day": 2500,
        "distance": "~600 km from Mumbai", "travel_time": "1 hr by flight",
        "highlight": "Calangute & Baga Beach, Dudhsagar Falls, Old Goa Churches",
        "image_keyword": "goa beach sunset palm trees waves",
        "famous_for": "Beaches, nightlife, seafood, and Portuguese architecture",
    },
    {
        "name": "Andaman Islands", "location": "Port Blair, Andaman & Nicobar",
        "tagline": "Crystal waters, pristine beaches, and untouched nature",
        "styles": ["beaches", "islands", "water-based", "adventure", "nature & landscape", "heritage sites"],
        "base_cost": 25000, "cost_per_day": 4000,
        "distance": "~1200 km from Chennai (by air)", "travel_time": "2.5 hrs by flight",
        "highlight": "Radhanagar Beach, Havelock Island, scuba diving, Cellular Jail",
        "image_keyword": "andaman beach clear turquoise water coral island",
        "famous_for": "Scuba diving, pristine beaches, and bioluminescent bays",
    },
    {
        "name": "Lakshadweep", "location": "Kavaratti, Lakshadweep",
        "tagline": "India's hidden paradise — coral islands and lagoons",
        "styles": ["beaches", "islands", "water-based", "nature & landscape"],
        "base_cost": 30000, "cost_per_day": 5000,
        "distance": "~400 km from Kochi (by sea/air)", "travel_time": "1.5 hrs by flight",
        "highlight": "Agatti Island, lagoon snorkeling, glass-bottom boat rides",
        "image_keyword": "lakshadweep lagoon coral reef turquoise island",
        "famous_for": "Coral reefs, crystal lagoons, and marine biodiversity",
    },
    {
        "name": "Pondicherry", "location": "Puducherry, India",
        "tagline": "French charm meets Indian soul by the Bay of Bengal",
        "styles": ["beaches", "culture & heritage", "heritage sites", "city life", "food & culinary", "museums & arts"],
        "base_cost": 5000, "cost_per_day": 1500,
        "distance": "~150 km from Chennai", "travel_time": "3 hrs by bus/train",
        "highlight": "Promenade Beach, Auroville, French Quarter, Sri Aurobindo Ashram",
        "image_keyword": "pondicherry french quarter beach colorful streets",
        "famous_for": "French architecture, spiritual retreats, and beach cafes",
    },
    {
        "name": "Varkala", "location": "Varkala, Kerala",
        "tagline": "Cliff-top beach paradise in God's Own Country",
        "styles": ["beaches", "nature & landscape", "temples & spiritual", "backwaters & lakes"],
        "base_cost": 7000, "cost_per_day": 1800,
        "distance": "~55 km from Thiruvananthapuram", "travel_time": "1.5 hrs",
        "highlight": "Varkala Cliff, Papanasam Beach, Janardanaswamy Temple",
        "image_keyword": "varkala cliff beach kerala sunset",
        "famous_for": "Red laterite cliffs, beach yoga, and Ayurvedic treatments",
    },

    # MOUNTAINS / HILL STATIONS
    {
        "name": "Manali", "location": "Manali, Himachal Pradesh",
        "tagline": "Snow-capped peaks, pine forests, and mountain magic",
        "styles": ["mountains", "hill stations", "adventure", "nature & landscape", "snow"],
        "base_cost": 12000, "cost_per_day": 2500,
        "distance": "~540 km from Delhi", "travel_time": "12 hrs bus or 1.5 hrs flight",
        "highlight": "Rohtang Pass, Solang Valley skiing, Hadimba Temple, Old Manali",
        "image_keyword": "manali mountains snow river himachal pradesh",
        "famous_for": "Snow sports, scenic beauty, and adventure activities",
    },
    {
        "name": "Shimla", "location": "Shimla, Himachal Pradesh",
        "tagline": "The Queen of Hills — colonial charm in the Himalayas",
        "styles": ["hill stations", "mountains", "culture & heritage", "nature & landscape"],
        "base_cost": 10000, "cost_per_day": 2000,
        "distance": "~370 km from Delhi", "travel_time": "8 hrs by bus",
        "highlight": "The Ridge, Jakhu Temple, Christ Church, Mall Road",
        "image_keyword": "shimla hill station colonial town himachal",
        "famous_for": "Toy train ride, colonial architecture, and apple orchards",
    },
    {
        "name": "Leh Ladakh", "location": "Leh, Ladakh",
        "tagline": "The roof of India — otherworldly landscapes and monasteries",
        "styles": ["mountains", "adventure", "nature & landscape", "culture & heritage", "snow"],
        "base_cost": 20000, "cost_per_day": 3500,
        "distance": "~1000 km from Delhi", "travel_time": "1.5 hrs by flight",
        "highlight": "Pangong Lake, Nubra Valley, Khardung La Pass, Thiksey Monastery",
        "image_keyword": "ladakh pangong lake monastery mountain desert",
        "famous_for": "Monastery treks, Pangong Lake, and high-altitude adventures",
    },
    {
        "name": "Darjeeling", "location": "Darjeeling, West Bengal",
        "tagline": "Tea gardens, toy trains, and Himalayan sunrises",
        "styles": ["hill stations", "nature & landscape", "culture & heritage"],
        "base_cost": 10000, "cost_per_day": 2000,
        "distance": "~600 km from Kolkata", "travel_time": "12 hrs by train",
        "highlight": "Tiger Hill sunrise, Batasia Loop, tea estate tours, Himalayan Railway",
        "image_keyword": "darjeeling tea plantation himalayan sunrise kanchenjunga",
        "famous_for": "Darjeeling tea, UNESCO toy train, and Kanchenjunga views",
    },
    {
        "name": "Munnar", "location": "Munnar, Kerala",
        "tagline": "Rolling tea hills and misty valleys of Kerala",
        "styles": ["hill stations", "nature & landscape", "forests & wildlife", "waterfalls", "backwaters & lakes"],
        "base_cost": 8000, "cost_per_day": 1800,
        "distance": "~580 km from Chennai", "travel_time": "9 hrs by bus",
        "highlight": "Tea Museum, Eravikulam National Park, Mattupetty Dam, Attukal Waterfalls",
        "image_keyword": "munnar tea plantation hills mist kerala green",
        "famous_for": "Tea and spice plantations, Neelakurinji flowers, wildlife",
    },
    {
        "name": "Ooty (Udhagamandalam)", "location": "Ooty, Tamil Nadu",
        "tagline": "Queen of Hill Stations in the Nilgiris",
        "styles": ["hill stations", "nature & landscape", "forests & wildlife"],
        "base_cost": 5000, "cost_per_day": 1500,
        "distance": "~560 km from Chennai", "travel_time": "8 hrs by bus",
        "highlight": "Ooty Lake, Botanical Gardens, Doddabetta Peak, Nilgiri Mountain Railway",
        "image_keyword": "ooty nilgiris hill station botanical garden lake",
        "famous_for": "Nilgiri Mountain Railway, rose gardens, and Toda villages",
    },
    {
        "name": "Kodaikanal", "location": "Kodaikanal, Tamil Nadu",
        "tagline": "Princess of Hill Stations — misty lakes and ancient forests",
        "styles": ["hill stations", "nature & landscape", "forests & wildlife", "backwaters & lakes", "waterfalls"],
        "base_cost": 5000, "cost_per_day": 1400,
        "distance": "~460 km from Chennai", "travel_time": "7 hrs by bus",
        "highlight": "Kodai Lake, Coaker's Walk, Pillar Rocks, Bryant Park, Pine Forest",
        "image_keyword": "kodaikanal lake mist hill station tamil nadu green",
        "famous_for": "Star-shaped lake, homemade chocolates, eucalyptus forests, and sunrise from Dolphin's Nose",
    },
    {
        "name": "Yelagiri", "location": "Yelagiri Hills, Tamil Nadu",
        "tagline": "Peaceful hill retreat just 3 hours from Chennai",
        "styles": ["hill stations", "nature & landscape", "adventure"],
        "base_cost": 3000, "cost_per_day": 1000,
        "distance": "~230 km from Chennai", "travel_time": "3.5 hrs by bus",
        "highlight": "Yelagiri Lake, Swami Malai Hills trek, Nature Park, 14-hairpin bend road",
        "image_keyword": "yelagiri hills lake tamil nadu green peaceful",
        "famous_for": "Budget-friendly weekend getaway, paragliding, trekking, rose garden",
    },
    {
        "name": "Yercaud", "location": "Yercaud, Tamil Nadu",
        "tagline": "The Jewel of the South — serene coffee plantations and lakes",
        "styles": ["hill stations", "nature & landscape"],
        "base_cost": 3500, "cost_per_day": 1000,
        "distance": "~360 km from Chennai", "travel_time": "5 hrs by bus",
        "highlight": "Yercaud Lake, Lady's Seat viewpoint, Bear's Cave, Killiyur Falls",
        "image_keyword": "yercaud lake coffee plantation hill station salem",
        "famous_for": "Coffee plantations, serene lake, orange groves, and Shevaroy Temple",
    },
    {
        "name": "Coorg (Kodagu)", "location": "Coorg, Karnataka",
        "tagline": "Scotland of India — coffee, mist, and waterfalls",
        "styles": ["hill stations", "nature & landscape", "forests & wildlife", "adventure", "waterfalls", "village/rural tourism"],
        "base_cost": 7000, "cost_per_day": 1600,
        "distance": "~490 km from Chennai", "travel_time": "8 hrs by bus",
        "highlight": "Abbey Falls, Raja's Seat, Dubare Elephant Camp, Namdroling Monastery",
        "image_keyword": "coorg coffee plantation mist waterfall karnataka green",
        "famous_for": "Coffee estates, spice plantations, river rafting, and Kodava cuisine",
    },
    {
        "name": "Wayanad", "location": "Wayanad, Kerala",
        "tagline": "Lush green hills, tribal heritage, and misty mornings",
        "styles": ["hill stations", "nature & landscape", "forests & wildlife", "adventure", "caves", "backwaters & lakes", "village/rural tourism"],
        "base_cost": 7000, "cost_per_day": 1600,
        "distance": "~640 km from Chennai", "travel_time": "10 hrs by bus",
        "highlight": "Edakkal Caves, Banasura Sagar Dam, Pookode Lake, Chembra Peak trek",
        "image_keyword": "wayanad hill station mist tea plantation kerala",
        "famous_for": "Ancient Edakkal cave carvings, bamboo rafting, and spice gardens",
    },

    {
        "name": "Mussoorie", "location": "Mussoorie, Uttarakhand",
        "tagline": "The Queen of Hills with panoramic Himalayan views",
        "styles": ["hill stations", "mountains", "nature & landscape", "adventure", "waterfalls"],
        "base_cost": 8000, "cost_per_day": 1800,
        "distance": "~290 km from Delhi", "travel_time": "6 hrs by road",
        "highlight": "Kempty Falls, Gun Hill, Lal Tibba, Camel's Back Road",
        "image_keyword": "mussoorie hill station valley himalayan view uttarakhand",
        "famous_for": "British-era architecture, Kempty Fall, and Mall Road views",
    },
    {
        "name": "Meghalaya", "location": "Shillong & Cherrapunji, Meghalaya",
        "tagline": "The abode of clouds — living root bridges and waterfalls",
        "styles": ["nature & landscape", "adventure", "forests & wildlife", "water-based", "waterfalls", "caves", "village/rural tourism", "backwaters & lakes"],
        "base_cost": 15000, "cost_per_day": 3000,
        "distance": "~1600 km from Delhi", "travel_time": "2.5 hrs by flight",
        "highlight": "Living Root Bridges, Nohkalikai Falls, Mawlynnong (cleanest village), Umiam Lake",
        "image_keyword": "meghalaya living root bridge waterfall mist green",
        "famous_for": "World's wettest place, double-decker root bridges, and pristine caves",
    },
    {
        "name": "Spiti Valley", "location": "Kaza, Himachal Pradesh",
        "tagline": "Middle land between India and Tibet — raw Himalayan beauty",
        "styles": ["mountains", "adventure", "nature & landscape", "culture & heritage", "heritage sites", "village/rural tourism", "backwaters & lakes"],
        "base_cost": 18000, "cost_per_day": 3500,
        "distance": "~450 km from Shimla", "travel_time": "12+ hrs by road",
        "highlight": "Key Monastery, Chandratal Lake, Kibber Village, fossil sites",
        "image_keyword": "spiti valley monastery himalaya barren mountain blue sky",
        "famous_for": "Buddhist monasteries, fossils at world's highest altitude, and star-gazing",
    },

    # DESERTS & HERITAGE
    {
        "name": "Jaisalmer", "location": "Jaisalmer, Rajasthan",
        "tagline": "The Golden City — sand dunes and medieval magic",
        "styles": ["deserts", "culture & heritage", "heritage sites", "nature & landscape", "adventure"],
        "base_cost": 10000, "cost_per_day": 2200,
        "distance": "~570 km from Jaipur", "travel_time": "10 hrs by train",
        "highlight": "Sam Sand Dunes, Jaisalmer Fort, Patwon Ki Haveli, desert safari",
        "image_keyword": "jaisalmer golden fort sand dunes desert rajasthan sunset",
        "famous_for": "Living fort, camel safaris, and Thar Desert sunsets",
    },
    {
        "name": "Rajasthan — Jaipur & Udaipur", "location": "Jaipur & Udaipur, Rajasthan",
        "tagline": "Royal grandeur, floating palaces, and desert heritage",
        "styles": ["culture & heritage", "heritage sites", "deserts", "city life", "food & culinary", "museums & arts", "backwaters & lakes"],
        "base_cost": 14000, "cost_per_day": 2800,
        "distance": "~280 km from Delhi to Jaipur", "travel_time": "5 hrs by Shatabdi",
        "highlight": "Hawa Mahal, Amer Fort, City Palace, Lake Pichola, Mehrangarh Fort",
        "image_keyword": "jaipur pink city hawa mahal udaipur lake palace rajasthan",
        "famous_for": "Pink City, Lake Palace, blue pottery, and Rajput history",
    },
    {
        "name": "Rann of Kutch", "location": "Bhuj, Gujarat",
        "tagline": "The Great White Desert — the world's largest salt flat",
        "styles": ["deserts", "nature & landscape", "culture & heritage", "heritage sites", "village/rural tourism"],
        "base_cost": 10000, "cost_per_day": 2200,
        "distance": "~400 km from Ahmedabad", "travel_time": "6 hrs by road",
        "highlight": "Rann Utsav festival, white salt flats, flamingo colonies, Banni grasslands",
        "image_keyword": "rann kutch white salt desert gujarat sunset festival",
        "famous_for": "White Rann at full moon, crafts of the Kutchi artisans, and Rann Utsav",
    },
    {
        "name": "Hampi", "location": "Hampi, Karnataka",
        "tagline": "Ruins of the Vijayanagara Empire — a UNESCO World Heritage Site",
        "styles": ["culture & heritage", "heritage sites", "adventure", "nature & landscape", "temples & spiritual"],
        "base_cost": 6000, "cost_per_day": 1500,
        "distance": "~350 km from Bangalore", "travel_time": "7 hrs by road or night train",
        "highlight": "Virupaksha Temple, Vittala Temple Stone Chariot, boulder landscape, banana plantations",
        "image_keyword": "hampi vijayanagara ruins temple boulders karnataka",
        "famous_for": "UNESCO ruins, unique boulder landscape, and sunrise views from Matanga Hill",
    },
    {
        "name": "Varanasi", "location": "Varanasi, Uttar Pradesh",
        "tagline": "The eternal city — ghats, spirituality, and the Ganges",
        "styles": ["culture & heritage", "heritage sites", "temples & spiritual", "food & culinary", "museums & arts"],
        "base_cost": 6000, "cost_per_day": 1500,
        "distance": "~800 km from Delhi", "travel_time": "10 hrs by Shatabdi or 1.5 hrs by flight",
        "highlight": "Dashashwamedh Ghat Aarti, Kashi Vishwanath Temple, Sarnath, Manikarnika Ghat",
        "image_keyword": "varanasi ghat ganges aarti ritual sunset spiritual",
        "famous_for": "Evening Ganga Aarti, boat rides at sunrise, and Banarasi silk sarees",
    },
    {
        "name": "Agra — Taj Mahal & Fatehpur Sikri", "location": "Agra, Uttar Pradesh",
        "tagline": "One of the Seven Wonders — a monument to eternal love",
        "styles": ["culture & heritage", "heritage sites", "city life", "food & culinary", "museums & arts"],
        "base_cost": 5000, "cost_per_day": 1500,
        "distance": "~200 km from Delhi", "travel_time": "2 hrs by Gatiman Express train",
        "highlight": "Taj Mahal at sunrise, Agra Fort, Fatehpur Sikri, Mehtab Bagh moonlight view",
        "image_keyword": "taj mahal agra sunrise reflection marble white",
        "famous_for": "Taj Mahal, Mughal architecture, and Petha sweet delicacy",
    },

    # NATURE / WILDLIFE
    {
        "name": "Kerala Backwaters", "location": "Alleppey (Alappuzha), Kerala",
        "tagline": "Float through a network of canals on a traditional houseboat",
        "styles": ["nature & landscape", "water-based", "backwaters & lakes", "forests & wildlife", "food & culinary", "village/rural tourism"],
        "base_cost": 12000, "cost_per_day": 3000,
        "distance": "~85 km from Kochi", "travel_time": "2 hrs by road",
        "highlight": "Houseboat cruise, Vembanad Lake, Kuttanad paddy fields, snake boat races",
        "image_keyword": "kerala backwaters houseboat canal coconut palm green",
        "famous_for": "Houseboat stays, labyrinthine canals, and Nehru Trophy boat race",
    },
    {
        "name": "Sundarbans", "location": "Gosaba, West Bengal",
        "tagline": "The world's largest mangrove forest — home of the Royal Bengal Tiger",
        "styles": ["forests & wildlife", "nature & landscape", "adventure"],
        "base_cost": 8000, "cost_per_day": 1800,
        "distance": "~100 km from Kolkata", "travel_time": "3 hrs by road + ferry",
        "highlight": "Tiger spotting, mangrove jungle safari, Sajnekhali Wildlife Sanctuary",
        "image_keyword": "sundarbans mangrove tiger bengal forest river boat",
        "famous_for": "Royal Bengal Tiger, UNESCO heritage mangroves, and unique ecosystem",
    },
    {
        "name": "Ranthambore National Park", "location": "Sawai Madhopur, Rajasthan",
        "tagline": "India's best tiger safari — spot tigers in a medieval fort setting",
        "styles": ["forests & wildlife", "adventure", "nature & landscape"],
        "base_cost": 12000, "cost_per_day": 2800,
        "distance": "~180 km from Jaipur", "travel_time": "3 hrs by road",
        "highlight": "Tiger jeep safari, Ranthambore Fort, lake-side sighting zones",
        "image_keyword": "ranthambore tiger safari jeep rajasthan national park",
        "famous_for": "Most photographed tigers in India, historical fort within park",
    },
    {
        "name": "Jim Corbett National Park", "location": "Ramnagar, Uttarakhand",
        "tagline": "India's oldest national park — a haven for tigers and elephants",
        "styles": ["forests & wildlife", "adventure", "nature & landscape"],
        "base_cost": 10000, "cost_per_day": 2200,
        "distance": "~280 km from Delhi", "travel_time": "6 hrs by road",
        "highlight": "Dhikala zone safari, elephant rides, Corbett Museum, Garjiya Devi Temple",
        "image_keyword": "jim corbett elephant safari tiger forest uttarakhand",
        "famous_for": "India's oldest tiger reserve, elephant safaris, and birdwatching",
    },
    {
        "name": "Kaziranga National Park", "location": "Golaghat, Assam",
        "tagline": "UNESCO World Heritage — home to 2/3 of the world's one-horned rhinos",
        "styles": ["forests & wildlife", "nature & landscape", "adventure"],
        "base_cost": 12000, "cost_per_day": 2500,
        "distance": "~250 km from Guwahati", "travel_time": "4 hrs by road",
        "highlight": "Elephant-back rhino safari, bird watching, tiger sighting, tea estates",
        "image_keyword": "kaziranga rhino elephant assam national park",
        "famous_for": "UNESCO World Heritage, highest density of one-horned rhinos",
    },

    # ADVENTURE / SPIRITUAL
    {
        "name": "Rishikesh", "location": "Rishikesh, Uttarakhand",
        "tagline": "Adventure capital of India — rafting, yoga, and Ganges",
        "styles": ["adventure", "temples & spiritual", "nature & landscape", "mountains"],
        "base_cost": 6000, "cost_per_day": 1500,
        "distance": "~240 km from Delhi", "travel_time": "5 hrs by road",
        "highlight": "River rafting, Laxman Jhula, Beatles Ashram, Ganga Aarti at Triveni Ghat",
        "image_keyword": "rishikesh river rafting ganga bridge spiritual yoga",
        "famous_for": "Yoga capital of the world, white water rafting, and ashrams",
    },
    {
        "name": "Amritsar", "location": "Amritsar, Punjab",
        "tagline": "The Golden Temple — a spiritual haven of gold and devotion",
        "styles": ["temples & spiritual", "culture & heritage", "heritage sites", "food & culinary", "museums & arts"],
        "base_cost": 6000, "cost_per_day": 1400,
        "distance": "~460 km from Delhi", "travel_time": "6 hrs by train",
        "highlight": "Golden Temple (Harmandir Sahib), Wagah Border ceremony, Jallianwala Bagh",
        "image_keyword": "amritsar golden temple reflection water spiritual sikh",
        "famous_for": "Golden Temple, langar (free community meal), and Wagah Border",
    },
    {
        "name": "Tirupati & Madurai", "location": "Tirupati, Andhra Pradesh",
        "tagline": "India's most visited pilgrimage and the city of the Meenakshi Temple",
        "styles": ["temples & spiritual", "culture & heritage", "heritage sites"],
        "base_cost": 5000, "cost_per_day": 1200,
        "distance": "~550 km from Chennai", "travel_time": "1.5 hrs by flight",
        "highlight": "Venkateswara Temple (world's richest), Meenakshi Amman Temple",
        "image_keyword": "tirupati temple gopuram south india spiritual",
        "famous_for": "Tirumala temple, laddu prasadam, and ancient temple architecture",
    },

    # CITY LIFE
    {
        "name": "Mumbai", "location": "Mumbai, Maharashtra",
        "tagline": "The city that never sleeps — Bollywood, bazaars, and beaches",
        "styles": ["city life", "culture & heritage", "heritage sites", "food & culinary", "beaches", "museums & arts"],
        "base_cost": 12000, "cost_per_day": 2800,
        "distance": "Hub city", "travel_time": "Direct",
        "highlight": "Marine Drive, Colaba Causeway, Bollywood Studio Tour, Dharavi",
        "image_keyword": "mumbai marine drive gateway india city skyline night",
        "famous_for": "Bollywood, street food (vada pav), and marine drive sunsets",
    },

    # INTERNATIONAL DESTINATIONS
    {
        "name": "Bali, Indonesia", "location": "Bali, Indonesia",
        "tagline": "Island of the Gods — temples, rice terraces, and surf",
        "styles": ["beaches", "islands", "temples & spiritual", "nature & landscape", "adventure", "food & culinary"],
        "base_cost": 35000, "cost_per_day": 6000,
        "distance": "~4 hrs by flight from major Indian cities", "travel_time": "4 hrs flight",
        "highlight": "Ubud rice terraces, Tanah Lot Temple, Seminyak Beach, Mount Batur",
        "image_keyword": "bali rice terrace temple beach indonesia tropical",
        "famous_for": "Temple ceremonies, rice terraces, surf culture, and yoga retreats",
        "international": True,
    },
    {
        "name": "Thailand — Bangkok & Phuket", "location": "Thailand",
        "tagline": "Land of smiles — golden temples, street food, and tropical beaches",
        "styles": ["beaches", "islands", "culture & heritage", "food & culinary", "city life", "adventure"],
        "base_cost": 30000, "cost_per_day": 5000,
        "distance": "~3 hrs from Chennai/Kolkata", "travel_time": "3-4 hrs flight",
        "highlight": "Grand Palace Bangkok, Phi Phi Islands, Thai street food, elephant sanctuary",
        "image_keyword": "thailand bangkok temple beach tropical islands",
        "famous_for": "Vibrant street food, Buddhist temples, and stunning islands",
        "international": True,
    },
    {
        "name": "Dubai, UAE", "location": "Dubai, UAE",
        "tagline": "Where the desert meets the sky — luxury and superlatives",
        "styles": ["city life", "adventure", "culture & heritage", "deserts", "water-based"],
        "base_cost": 45000, "cost_per_day": 8000,
        "distance": "~3 hrs from major Indian cities", "travel_time": "3 hrs flight",
        "highlight": "Burj Khalifa, Dubai Mall, Desert Safari, Palm Jumeirah",
        "image_keyword": "dubai burj khalifa skyline desert luxury",
        "famous_for": "World's tallest building, tax-free shopping, and desert safaris",
        "international": True,
    },
    {
        "name": "Maldives", "location": "Malé, Maldives",
        "tagline": "Overwater bungalows, coral reefs, and infinite blue",
        "styles": ["beaches", "islands", "water-based", "nature & landscape"],
        "base_cost": 60000, "cost_per_day": 10000,
        "distance": "~3 hrs from South India", "travel_time": "3 hrs flight",
        "highlight": "Overwater villas, snorkeling with manta rays, bioluminescent beaches",
        "image_keyword": "maldives overwater bungalow turquoise ocean coral reef",
        "famous_for": "Most luxurious island getaway with unparalleled marine life",
        "international": True,
    },
    {
        "name": "Nepal — Kathmandu & Pokhara", "location": "Nepal",
        "tagline": "Roof of the world — Himalayas, temples, and trekking",
        "styles": ["mountains", "adventure", "temples & spiritual", "nature & landscape", "snow"],
        "base_cost": 18000, "cost_per_day": 3000,
        "distance": "~1.5 hrs from Delhi/Kolkata", "travel_time": "1.5 hrs flight",
        "highlight": "Everest Base Camp, Boudhanath Stupa, Phewa Lake, Annapurna Circuit",
        "image_keyword": "nepal himalayas everest monastery kathmandu temple",
        "famous_for": "Everest, Himalayan trekking, Buddhist culture, and adventure sports",
        "international": True,
    },
    {
        "name": "Sri Lanka", "location": "Sri Lanka",
        "tagline": "Pearl of the Indian Ocean — beaches, ruins, and elephants",
        "styles": ["beaches", "culture & heritage", "heritage sites", "forests & wildlife", "nature & landscape", "temples & spiritual"],
        "base_cost": 22000, "cost_per_day": 4000,
        "distance": "~1 hr from Chennai", "travel_time": "1 hr flight",
        "highlight": "Sigiriya Rock Fortress, Elephant Orphanage, Mirissa beach, Temple of Tooth",
        "image_keyword": "sri lanka sigiriya rock fortress elephant beach temple",
        "famous_for": "Ancient ruins, friendly elephants, Ceylon tea, and whale watching",
        "international": True,
    },
    {
        "name": "Singapore", "location": "Singapore",
        "tagline": "The Lion City — futuristic, multicultural, and immaculate",
        "styles": ["city life", "food & culinary", "nature & landscape", "water-based", "museums & arts"],
        "base_cost": 40000, "cost_per_day": 7000,
        "distance": "~5 hrs from major Indian cities", "travel_time": "5 hrs flight",
        "highlight": "Gardens by the Bay, Marina Bay Sands, Sentosa Island, hawker centers",
        "image_keyword": "singapore marina bay sands garden city skyline night",
        "famous_for": "Futuristic architecture, legendary hawker food, and Changi airport",
        "international": True,
    },
    {
        "name": "Vietnam — Hanoi & Ha Long Bay", "location": "Vietnam",
        "tagline": "Emerald bay, lantern-lit cities, and banh mi paradise",
        "styles": ["nature & landscape", "culture & heritage", "food & culinary", "adventure", "water-based"],
        "base_cost": 28000, "cost_per_day": 4500,
        "distance": "~4 hrs from Delhi", "travel_time": "4 hrs flight",
        "highlight": "Ha Long Bay cruise, Hoi An Old Town, Hanoi street food, rice terraces",
        "image_keyword": "vietnam ha long bay boat karst emerald water",
        "famous_for": "Halong Bay cruises, lantern festivals, French-Vietnamese cuisine",
        "international": True,
    },
    {
        "name": "Japan — Tokyo & Kyoto", "location": "Tokyo & Kyoto, Japan",
        "tagline": "Where ancient tradition meets cutting-edge technology",
        "styles": ["culture & heritage", "heritage sites", "city life", "food & culinary", "temples & spiritual", "museums & arts", "adventure"],
        "base_cost": 55000, "cost_per_day": 9000,
        "distance": "~7 hrs by flight", "travel_time": "7 hrs flight",
        "highlight": "Tokyo Tower, Fushimi Inari Shrine, Mt. Fuji, Shibuya Crossing, Akihabara",
        "image_keyword": "japan tokyo temple cherry blossom fuji mountain",
        "famous_for": "Cherry blossoms, sushi & ramen, bullet trains, and ancient temples",
        "international": True,
    },
    {
        "name": "Turkey — Istanbul & Cappadocia", "location": "Istanbul & Cappadocia, Turkey",
        "tagline": "Where East meets West — hot air balloons and ancient empires",
        "styles": ["culture & heritage", "heritage sites", "adventure", "city life", "food & culinary", "museums & arts"],
        "base_cost": 40000, "cost_per_day": 6500,
        "distance": "~5 hrs by flight", "travel_time": "5 hrs flight",
        "highlight": "Hagia Sophia, Cappadocia balloon rides, Blue Mosque, Grand Bazaar",
        "image_keyword": "turkey cappadocia hot air balloon istanbul mosque",
        "famous_for": "Hot air balloon rides, Byzantine architecture, Turkish cuisine",
        "international": True,
    },
    {
        "name": "Greece — Athens & Santorini", "location": "Athens & Santorini, Greece",
        "tagline": "Whitewashed islands, ancient ruins, and Mediterranean sunsets",
        "styles": ["beaches", "islands", "culture & heritage", "heritage sites", "city life", "food & culinary"],
        "base_cost": 50000, "cost_per_day": 8000,
        "distance": "~7 hrs by flight", "travel_time": "7 hrs flight",
        "highlight": "Acropolis of Athens, Santorini blue domes, Mykonos nightlife, Meteora monasteries",
        "image_keyword": "greece santorini blue dome white church mediterranean sea",
        "famous_for": "Aegean island hopping, ancient Greek ruins, and world-class sunsets",
        "international": True,
    },
    {
        "name": "Switzerland — Zurich & Interlaken", "location": "Switzerland",
        "tagline": "The land of Alps, chocolate, and pristine lakes",
        "styles": ["mountains", "snow", "nature & landscape", "adventure", "backwaters & lakes", "city life"],
        "base_cost": 70000, "cost_per_day": 12000,
        "distance": "~8 hrs by flight", "travel_time": "8 hrs flight",
        "highlight": "Jungfraujoch, Lake Lucerne, Matterhorn, Swiss Alps railway, Interlaken paragliding",
        "image_keyword": "switzerland alps snow mountain lake zurich green village",
        "famous_for": "Swiss Alps, chocolate, cheese, luxury watches, and scenic train rides",
        "international": True,
    },
    {
        "name": "Egypt — Cairo & Luxor", "location": "Cairo & Luxor, Egypt",
        "tagline": "Land of the Pharaohs — pyramids, temples, and the Nile",
        "styles": ["culture & heritage", "heritage sites", "deserts", "adventure", "museums & arts"],
        "base_cost": 35000, "cost_per_day": 5500,
        "distance": "~5 hrs by flight", "travel_time": "5 hrs flight",
        "highlight": "Great Pyramids of Giza, Sphinx, Valley of the Kings, Nile cruise, Karnak Temple",
        "image_keyword": "egypt pyramids giza sphinx desert cairo ancient",
        "famous_for": "Ancient pyramids, Pharaonic tombs, Nile River cruises, and hieroglyphs",
        "international": True,
    },
    {
        "name": "Malaysia — Kuala Lumpur & Langkawi", "location": "Malaysia",
        "tagline": "Twin towers, tropical islands, and a melting pot of cultures",
        "styles": ["city life", "beaches", "islands", "food & culinary", "nature & landscape", "adventure"],
        "base_cost": 25000, "cost_per_day": 4000,
        "distance": "~4 hrs by flight", "travel_time": "4 hrs flight",
        "highlight": "Petronas Twin Towers, Langkawi Sky Bridge, Batu Caves, Penang street food",
        "image_keyword": "malaysia kuala lumpur petronas towers langkawi beach tropical",
        "famous_for": "Twin towers, Langkawi beaches, multicultural food, and rainforest canopy walks",
        "international": True,
    },
    {
        "name": "Cambodia — Siem Reap", "location": "Siem Reap, Cambodia",
        "tagline": "Home of Angkor Wat — the world's largest religious monument",
        "styles": ["culture & heritage", "heritage sites", "temples & spiritual", "adventure", "food & culinary", "village/rural tourism"],
        "base_cost": 20000, "cost_per_day": 3000,
        "distance": "~5 hrs by flight", "travel_time": "5 hrs flight (via Bangkok)",
        "highlight": "Angkor Wat sunrise, Ta Prohm (Tomb Raider temple), Tonle Sap floating village",
        "image_keyword": "cambodia angkor wat temple ruins sunrise ancient",
        "famous_for": "Angkor Wat, ancient Khmer ruins, and vibrant pub street nightlife",
        "international": True,
    },
    {
        "name": "Morocco — Marrakech & Sahara", "location": "Marrakech, Morocco",
        "tagline": "Vibrant souks, Saharan dunes, and Moroccan magic",
        "styles": ["deserts", "culture & heritage", "heritage sites", "adventure", "food & culinary", "city life", "village/rural tourism"],
        "base_cost": 35000, "cost_per_day": 5000,
        "distance": "~9 hrs by flight", "travel_time": "9 hrs flight",
        "highlight": "Jemaa el-Fnaa square, Sahara desert camp, Atlas Mountains, Medina of Fez",
        "image_keyword": "morocco marrakech sahara desert camel medina souk",
        "famous_for": "Sahara camel treks, colourful medinas, tagine cuisine, and riads",
        "international": True,
    },
    {
        "name": "South Korea — Seoul & Jeju", "location": "Seoul & Jeju Island, South Korea",
        "tagline": "K-pop, ancient palaces, and volcanic island beauty",
        "styles": ["city life", "culture & heritage", "heritage sites", "food & culinary", "nature & landscape", "islands", "museums & arts"],
        "base_cost": 45000, "cost_per_day": 7500,
        "distance": "~6 hrs by flight", "travel_time": "6 hrs flight",
        "highlight": "Gyeongbokgung Palace, Jeju Hallasan, Myeongdong, DMZ tour, Korean BBQ streets",
        "image_keyword": "south korea seoul palace cherry blossom jeju island",
        "famous_for": "K-pop culture, Korean BBQ, ancient palaces, and Jeju volcanic island",
        "international": True,
    },
    {
        "name": "Australia — Sydney & Melbourne", "location": "Sydney & Melbourne, Australia",
        "tagline": "Opera House, Great Barrier Reef, and endless coastline",
        "styles": ["city life", "beaches", "nature & landscape", "adventure", "food & culinary", "museums & arts", "forests & wildlife"],
        "base_cost": 80000, "cost_per_day": 12000,
        "distance": "~10 hrs by flight", "travel_time": "10 hrs flight",
        "highlight": "Sydney Opera House, Great Barrier Reef, Twelve Apostles, Blue Mountains",
        "image_keyword": "australia sydney opera house harbour bridge beach reef",
        "famous_for": "Sydney Opera House, Great Barrier Reef, unique wildlife, and surf culture",
        "international": True,
    },
    {
        "name": "New Zealand", "location": "Auckland & Queenstown, New Zealand",
        "tagline": "Middle-earth landscapes — mountains, fjords, and adventure capital",
        "styles": ["mountains", "adventure", "nature & landscape", "forests & wildlife", "backwaters & lakes", "snow"],
        "base_cost": 85000, "cost_per_day": 13000,
        "distance": "~12 hrs by flight", "travel_time": "12 hrs flight",
        "highlight": "Milford Sound, Queenstown bungee jump, Hobbiton, Franz Josef Glacier",
        "image_keyword": "new zealand milford sound mountains fjord green landscape",
        "famous_for": "Lord of the Rings filming locations, bungee jumping, and pristine fjords",
        "international": True,
    },
    {
        "name": "Spain — Barcelona & Madrid", "location": "Barcelona & Madrid, Spain",
        "tagline": "Flamenco, Gaudí, tapas, and Mediterranean vibes",
        "styles": ["city life", "culture & heritage", "heritage sites", "beaches", "food & culinary", "museums & arts", "adventure"],
        "base_cost": 55000, "cost_per_day": 8500,
        "distance": "~9 hrs by flight", "travel_time": "9 hrs flight",
        "highlight": "Sagrada Familia, Alhambra Palace, Park Güell, La Rambla, Flamenco shows",
        "image_keyword": "spain barcelona sagrada familia beach mediterranean",
        "famous_for": "Gaudí's architecture, tapas culture, flamenco, and La Liga football",
        "international": True,
    },
    {
        "name": "Italy — Rome & Venice", "location": "Rome & Venice, Italy",
        "tagline": "Eternal city, floating canals, and the birthplace of the Renaissance",
        "styles": ["culture & heritage", "heritage sites", "city life", "food & culinary", "museums & arts", "backwaters & lakes"],
        "base_cost": 60000, "cost_per_day": 9500,
        "distance": "~8 hrs by flight", "travel_time": "8 hrs flight",
        "highlight": "Colosseum, Venice gondola rides, Vatican City, Trevi Fountain, Leaning Tower of Pisa",
        "image_keyword": "italy rome colosseum venice canal gondola florence",
        "famous_for": "Ancient Roman ruins, Venetian canals, pasta & pizza, and Renaissance art",
        "international": True,
    },
    {
        "name": "Iceland — Reykjavik", "location": "Reykjavik, Iceland",
        "tagline": "Land of fire and ice — Northern Lights and volcanic wonders",
        "styles": ["nature & landscape", "adventure", "snow", "mountains", "waterfalls"],
        "base_cost": 90000, "cost_per_day": 15000,
        "distance": "~10 hrs by flight", "travel_time": "10 hrs flight (via Europe)",
        "highlight": "Northern Lights, Blue Lagoon, Golden Circle, Jökulsárlón Glacier Lagoon",
        "image_keyword": "iceland northern lights waterfall glacier volcanic landscape",
        "famous_for": "Aurora Borealis, geothermal hot springs, glaciers, and whale watching",
        "international": True,
    },
    {
        "name": "Mexico — Cancún & Mexico City", "location": "Cancún & Mexico City, Mexico",
        "tagline": "Ancient Mayan ruins, turquoise Caribbean, and vibrant culture",
        "styles": ["beaches", "culture & heritage", "heritage sites", "adventure", "food & culinary", "city life"],
        "base_cost": 50000, "cost_per_day": 7000,
        "distance": "~20 hrs by flight", "travel_time": "20 hrs flight (with stopover)",
        "highlight": "Chichén Itzá pyramid, Cancún beaches, Cenote swimming, Street tacos, Lucha Libre",
        "image_keyword": "mexico cancun beach chichen itza pyramid mayan ruins",
        "famous_for": "Mayan pyramids, Caribbean beaches, cenotes for diving, and Mexican street food",
        "international": True,
    },
    {
        "name": "London, UK", "location": "London, United Kingdom",
        "tagline": "Royal palaces, world-class museums, and British charm",
        "styles": ["city life", "culture & heritage", "heritage sites", "museums & arts", "food & culinary"],
        "base_cost": 65000, "cost_per_day": 11000,
        "distance": "~9 hrs by flight", "travel_time": "9 hrs flight",
        "highlight": "Big Ben, Tower of London, British Museum, Buckingham Palace, West End shows",
        "image_keyword": "london big ben tower bridge palace british skyline",
        "famous_for": "Royal family heritage, free world-class museums, and West End theatre",
        "international": True,
    },
    {
        "name": "Paris, France", "location": "Paris, France",
        "tagline": "City of Love — art, fashion, and the Eiffel Tower",
        "styles": ["city life", "culture & heritage", "heritage sites", "museums & arts", "food & culinary"],
        "base_cost": 60000, "cost_per_day": 10000,
        "distance": "~9 hrs by flight", "travel_time": "9 hrs flight",
        "highlight": "Eiffel Tower, Louvre Museum, Champs-Élysées, Montmartre, Seine cruise",
        "image_keyword": "paris eiffel tower seine river louvre french architecture",
        "famous_for": "Eiffel Tower, Louvre art museum, French cuisine, and romantic ambiance",
        "international": True,
    },
]


class GeminiAIService:
    """
    Main AI service — uses the new google-genai SDK v1.x.
    Falls back to intelligent static matching if no API key is configured.
    """

    def __init__(self):
        self.available = False
        self.client = None
        self._configure()

    def _configure(self):
        """Re-read API key and initialize client. Called per-request."""
        load_dotenv(override=True)
        key = _read_api_key()
        if key:
            client = _build_genai_client(key)
            if client:
                self.client = client
                self.available = True
                print(f"[AI] ✅ Gemini AI ready (key: {key[:8]}...)")
                return
        self.client = None
        self.available = False
        print("[AI] ⚠️  No valid Gemini API key — using smart fallback mode")
        print("[AI]    Get a free key at: https://aistudio.google.com/app/apikey")
        print("[AI]    Then add to .env: GEMINI_API_KEY=AIzaSy...")

    def _call_gemini(self, prompt: str) -> str | None:
        """Call the Gemini model and return raw text, or None on failure."""
        try:
            from google import genai
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            return response.text
        except Exception as e:
            print(f"[AI] Gemini call error: {e}")
            traceback.print_exc()
            return None

    def _clean_json(self, text: str):
        """Extract JSON object or array from Gemini response text."""
        if not text:
            return None
        # Strip markdown code fences
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        # Direct parse
        try:
            return json.loads(text)
        except Exception:
            pass
        # Extract largest JSON block
        for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
        return None

    # ─────────────────────────────────────────────────────────
    #  PUBLIC: RECOMMENDATIONS
    # ─────────────────────────────────────────────────────────

    def get_travel_recommendations(self, user_prefs: dict) -> dict:
        """
        Main entry point — returns recommendations dict always.
        Tries real Gemini AI first, falls back to intelligent static matching.
        """
        self._configure()

        if self.available:
            result = self._get_ai_recommendations(user_prefs)
            if result and result.get('recommendations'):
                print(f"[AI] ✅ Gemini returned {len(result['recommendations'])} destinations")
                return result
            print("[AI] Gemini response was empty — falling back to static database")

        return self._get_fallback_recommendations(user_prefs)

    def _get_ai_recommendations(self, prefs: dict) -> dict | None:
        """Build the prompt and call Gemini for recommendations."""
        styles = prefs.get('destination_styles', [])
        styles_str = ', '.join(styles) if styles else 'mixed destinations (beaches, mountains, nature, culture)'
        currency = prefs.get('currency', 'INR')
        budget = prefs.get('budget', 50000)
        num_days = prefs.get('num_days', 5)
        from_loc = prefs.get('from_location', 'India')
        medium = prefs.get('travel_medium', 'any')
        is_group = prefs.get('travel_type') == 'group'
        group_size = prefs.get('group_size', 1) if is_group else 1
        group_info = f"group of {group_size} people" if is_group else "solo traveler (1 person)"
        food_accom = prefs.get('food_accommodation', 'with')

        travel_scope = (
            "WITHIN INDIA ONLY — do NOT suggest international destinations"
            if prefs.get('travel_scope') == 'within_country'
            else "can be international destinations worldwide"
        )

        # Build travel-medium-specific cost instructions
        if medium == 'travel_agency':
            cost_instruction = f"""TRAVEL MODE: TRAVEL AGENCY PACKAGE
The user wants a TRAVEL AGENCY PACKAGE. The estimated_total_cost should be the TOTAL PACKAGE COST 
that a travel agency would charge, including transport, accommodation, food, sightseeing, and guide.
Search for ACTUAL travel agency package prices from popular agencies like MakeMyTrip, Yatra, IRCTC tourism,
state tourism packages for {num_days} days trips from {from_loc}.
This is THE ONLY mode where you should quote package prices."""
        elif medium == 'bus':
            cost_instruction = f"""TRAVEL MODE: BUS (Individual Travel — NOT package tour)
The user is traveling INDEPENDENTLY by bus. DO NOT show travel agency package prices.
Calculate costs as an INDIVIDUAL BUDGET TRAVELER would spend:
- Transport: Search for ACTUAL government bus (TNSTC, KSRTC, APSRTC, etc.) and private bus ticket prices from {from_loc}. 
  Example: Chennai to Ooty by government bus = INR 400-600, private sleeper = INR 700-1000.
- Accommodation: Budget lodges, dormitories, OYO rooms (INR 400-1200/night for budget).
- Food: Local restaurants, dhabas, street food (INR 150-300/day for budget meals).
- Sightseeing: Entry fees to tourist spots, local auto fares.
Keep costs REALISTIC for a budget backpacker/individual traveler using public bus transport."""
        elif medium == 'train':
            cost_instruction = f"""TRAVEL MODE: TRAIN (Individual Travel — NOT package tour)
The user is traveling INDEPENDENTLY by train. DO NOT show travel agency package prices.
Calculate costs as an INDIVIDUAL TRAVELER would spend:
- Transport: Search for ACTUAL Indian Railways ticket prices from {from_loc}.
  Use Sleeper class / 3AC / 2AC prices based on budget. Example: Chennai to Coimbatore sleeper = INR 200-350, 3AC = INR 600-900.
- Accommodation: Budget hotels, lodges, OYO rooms (INR 400-1500/night for budget).
- Food: Local restaurants, station food, street food (INR 150-400/day).
- Sightseeing: Entry fees, local transport (auto/bus) at destination.
Keep costs REALISTIC for individual train travelers, NOT tour packages."""
        elif medium == 'flight':
            cost_instruction = f"""TRAVEL MODE: FLIGHT (Individual Travel — NOT package tour)
The user is traveling INDEPENDENTLY by flight. DO NOT show travel agency package prices.
Calculate costs as an INDIVIDUAL TRAVELER would spend:
- Transport: Search for ACTUAL economy flight ticket prices from {from_loc} (IndiGo, SpiceJet, Air India, etc.).
  Example: Chennai to Goa one-way = INR 2500-5000 depending on advance booking.
- Accommodation: Budget to mid-range hotels (INR 800-2500/night).
- Food: Local restaurants (INR 200-500/day).
- Sightseeing: Entry fees, cab/auto at destination.
Keep costs REALISTIC for an individual flight traveler, NOT tour packages."""
        else:
            cost_instruction = f"""TRAVEL MODE: ANY (Individual Travel — NOT package tour)
Calculate costs for the CHEAPEST available individual transport option (bus, train, or flight).
DO NOT use travel agency/tour package prices. Show raw individual travel costs:
- Transport: Actual bus/train/flight ticket costs from {from_loc}
- Accommodation: Budget lodges/hotels  
- Food: Local meals
- Sightseeing: Entry fees, local transport"""

        # Build food/accommodation instruction
        if food_accom == 'with':
            food_instruction = """BUDGET INCLUDES: Transport + Accommodation + Food + Sightseeing = estimated_total_cost
Include realistic accommodation (budget lodges/hotels) and food (local restaurants/dhabas) in the total."""
        else:
            food_instruction = """BUDGET EXCLUDES food & accommodation. estimated_total_cost = Transport + Sightseeing ONLY.
The user arranges their own food and stay. Do NOT include hotel or food costs in estimated_total_cost."""

        prompt = f"""You are an expert AI travel analyst who recommends REAL, AFFORDABLE tourist destinations based on CURRENT 2025-2026 data.

TRAVELER PROFILE:
- Name: {prefs.get('name', 'Traveler')}
- Total Budget: {currency} {budget} (ENTIRE trip for {group_info})
- Travel Scope: {travel_scope}
- Type: {group_info}
- Duration: {num_days} days
- Departing From: {from_loc}
- Preferred Destination Styles: {styles_str}

{cost_instruction}

{food_instruction}

YOUR CORE MISSION:
Use Google Search to find REAL, CURRENT tourist destinations and ACTUAL 2025-2026 travel costs.
Think like a LOCAL TRAVELER — search for real bus/train/flight ticket prices, budget hotel rates, 
and local food costs. NOT online tour package prices (unless user selected travel_agency).

IMPORTANT COST GUIDELINES:
- Search the internet for REAL ticket prices (e.g., "{from_loc} to Ooty bus ticket price 2025")
- Search for budget hotel/lodge prices at each destination
- The total cost should be what a REAL person would actually spend, not inflated tour prices
- For nearby destinations (< 300 km), transport cost should be realistically low (bus: INR 200-800, train: INR 150-600)
- Prioritize destinations CLOSEST to {from_loc} first for low budgets
- A solo traveler with INR 3000-7000 for 2-3 days CAN visit hill stations near their city by bus/train

YOUR TASK — provide two groups of recommendations:

GROUP 1 — WITHIN BUDGET (mark "within_budget": true):
  Find 5-6 real tourist destinations that:
  • STRICTLY match: {styles_str}
  • estimated_total_cost ≤ {currency} {budget}
  • Are reachable from {from_loc} by {medium}
  • Cost calculated for {num_days} days for {group_info}
  • Start with NEAREST affordable destinations, then expand outward
  • For low budgets (< INR 10000), focus on destinations within 200-500 km of {from_loc}

GROUP 2 — BEYOND BUDGET / ASPIRATIONAL (mark "within_budget": false):
  Find 2-3 destinations that:
  • Cost 20-50% MORE than budget ({currency} {int(float(budget)*1.2)} to {currency} {int(float(budget)*1.5)})
  • Still match the styles but may be further away or more premium
  • Include "over_budget_note" explaining why the extra spend is worth it
  • These can be in other states or further locations

CRITICAL RULES:
- {travel_scope}
- All costs in {currency}, based on REAL 2025-2026 prices found via internet search
- Show INDIVIDUAL traveler costs, NOT travel agency packages (unless travel_agency mode)
- estimated_total_cost must reflect what a real person would ACTUALLY spend
- Include cost_per_day as a realistic daily spending figure

Return ONLY valid minified JSON (no markdown, no code blocks, no explanations):
{{"recommendations":[{{"id":1,"name":"Destination","location":"City, State/Country","tagline":"Exciting 1-line description","distance_from_start":"{from_loc} to destination distance in km","travel_time":"X hours by {medium}","within_budget":true,"estimated_total_cost":3500,"currency":"{currency}","cost_per_day":1200,"best_for":["Hill Stations","Nature"],"highlight":"Top 3 must-see attractions","image_keyword":"scenic landscape keyword for image search","famous_for":"What makes this place unique and special","transport_cost":"Round-trip {medium} cost from {from_loc}","over_budget_note":null}},...more...],"ai_summary":"Personalized 2-3 line summary for {prefs.get('name','the traveler')} explaining the recommendations."}}"""

        raw = self._call_gemini(prompt)
        if not raw:
            return None
        data = self._clean_json(raw)
        if not data or 'recommendations' not in data:
            print(f"[AI] Could not parse Gemini response. Raw (first 500 chars): {raw[:500]}")
            return None
        # Validate each recommendation has required fields
        valid = []
        for rec in data.get('recommendations', []):
            if rec.get('name') and rec.get('estimated_total_cost') is not None:
                rec.setdefault('within_budget', rec.get('estimated_total_cost', 0) <= float(budget))
                rec.setdefault('currency', currency)
                rec.setdefault('over_budget_note', None)
                rec.setdefault('best_for', [])
                valid.append(rec)
        data['recommendations'] = valid
        return data

    # ─────────────────────────────────────────────────────────
    #  PUBLIC: DESTINATION DETAILS
    # ─────────────────────────────────────────────────────────

    def get_destination_details(self, destination_name: str, user_prefs: dict) -> dict:
        """Get comprehensive details for a specific destination."""
        self._configure()
        if self.available:
            result = self._get_ai_destination_details(destination_name, user_prefs)
            if result:
                return result
        return self._get_fallback_destination_details(destination_name, user_prefs)

    def _get_ai_destination_details(self, destination_name, prefs):
        currency = prefs.get('currency', 'INR')
        num_days = prefs.get('num_days', 5)
        from_loc = prefs.get('from_location', 'India')
        budget = prefs.get('budget', 50000)
        travel_type = prefs.get('travel_type', 'solo')
        group_size = prefs.get('group_size', 1) if travel_type == 'group' else 1
        medium = prefs.get('travel_medium', 'any')
        food_accom = prefs.get('food_accommodation', 'with')

        # Travel medium context for cost breakdown
        if medium == 'travel_agency':
            medium_note = "Show TRAVEL AGENCY PACKAGE costs in the cost breakdown."
        else:
            medium_note = f"Show INDIVIDUAL traveler costs for {medium} transport. Use real {medium} ticket prices, NOT tour package prices. Search for actual ticket costs."

        prompt = f"""You are a comprehensive travel guide expert providing real, detailed information about "{destination_name}".

Traveler context:
- Coming from: {from_loc}
- Budget: {currency} {budget} total for {num_days} days
- Group: {group_size} person(s) traveling {travel_type}
- Travel mode: {medium}
- {medium_note}

Provide REAL, ACCURATE, SPECIFIC, and CURRENT 2025-2026 information by searching the internet. Use actual names of places, restaurants, hotels, and current ticket prices.
For the cost_breakdown, use REALISTIC individual travel costs (actual bus/train/flight tickets, budget lodges, local food) NOT inflated tour package prices.

IMPORTANT for events_festivals: Search the internet for REAL, WELL-KNOWN festivals and cultural events that actually take place at or near "{destination_name}". Include the exact months they occur, what rituals/activities happen, and why travelers should attend. These must be GENUINE festivals, NOT generic placeholders like "Local Festival" or "Cultural Event".

Return ONLY valid minified JSON (no markdown):
{{"name":"{destination_name}","full_location":"Full city, state/country","distance_from_start":"Exact distance from {from_loc}","overview":"Rich 4-sentence description of why this place is amazing and unique","famous_for":["specific thing 1","specific thing 2","specific thing 3","specific thing 4","specific thing 5"],"best_season":"Specific best months with reason e.g. Oct-Mar (cool, dry weather perfect for sightseeing)","tourist_spots":[{{"name":"Real Attraction Name","description":"What makes it special and must-visit","entry_fee":"{currency} amount or Free"}},...5 spots],"food_spots":[{{"name":"Real Restaurant or Food Street Name","specialty":"Specific local dish","avg_cost":"{currency} per person"}},...4 spots],"travel_options":[{{"mode":"Flight/Train/Bus","duration":"X hrs","cost":"{currency} approx one-way","from":"{from_loc}"}},...3 options],"accommodation":[{{"type":"Budget/Mid-range/Luxury","name":"Real hotel or hostel example","cost_per_night":"{currency} amount"}},...3 options],"events_festivals":[{{"name":"Actual Festival Name (e.g. Onam, Pushkar Camel Fair, Sunburn Festival)","month":"Specific months (e.g. August-September, November, December)","description":"2-3 sentence vivid description of what happens — rituals, performances, food, atmosphere"}},...4 to 5 REAL festivals/cultural events],"cost_breakdown":{{"travel_to_destination":"{currency} round trip from {from_loc}","accommodation_total":"{currency} for {num_days} nights","food_total":"{currency} for {num_days} days","sightseeing_total":"{currency}","miscellaneous":"{currency}","grand_total":"{currency}"}},"travel_tips":["Tip 1: specific actionable tip","Tip 2: best time to visit specific places","Tip 3: what to avoid","Tip 4: local cultural etiquette"],"local_transport":"Specific transport options with costs e.g. Auto-rickshaw: INR 20-50/km, Ola/Uber available"}}"""

        raw = self._call_gemini(prompt)
        if not raw:
            return None
        return self._clean_json(raw)

    # ─────────────────────────────────────────────────────────
    #  PUBLIC: LOCATION SUGGESTIONS
    # ─────────────────────────────────────────────────────────

    def get_location_suggestions(self, query: str) -> list:
        """Autocomplete location suggestions."""
        self._configure()
        if self.available:
            prompt = f"""List exactly 6 real Indian cities or popular tourist locations matching "{query}".
Return ONLY a JSON array of strings, no other text:
["Location 1, State", "Location 2, State", ...]"""
            raw = self._call_gemini(prompt)
            if raw:
                data = self._clean_json(raw)
                if isinstance(data, list):
                    return data[:6]
        return self._get_fallback_locations(query)

    def _get_fallback_locations(self, query: str) -> list:
        """Static location autocomplete."""
        locations = [
            "Mumbai, Maharashtra", "Delhi, NCR", "Bangalore, Karnataka",
            "Chennai, Tamil Nadu", "Kolkata, West Bengal", "Hyderabad, Telangana",
            "Pune, Maharashtra", "Ahmedabad, Gujarat", "Jaipur, Rajasthan",
            "Kochi, Kerala", "Goa", "Surat, Gujarat", "Lucknow, Uttar Pradesh",
            "Coimbatore, Tamil Nadu", "Mysore, Karnataka", "Agra, Uttar Pradesh",
            "Varanasi, Uttar Pradesh", "Rishikesh, Uttarakhand", "Manali, Himachal Pradesh",
            "Shimla, Himachal Pradesh", "Darjeeling, West Bengal", "Gangtok, Sikkim",
            "Leh, Ladakh", "Srinagar, J&K", "Amritsar, Punjab", "Chandigarh",
            "Udaipur, Rajasthan", "Jodhpur, Rajasthan", "Jaisalmer, Rajasthan",
            "Munnar, Kerala", "Alleppey, Kerala", "Pondicherry",
            "Ooty, Tamil Nadu", "Kodaikanal, Tamil Nadu", "Hampi, Karnataka",
        ]
        q = query.lower()
        return [loc for loc in locations if q in loc.lower()][:6]

    # ─────────────────────────────────────────────────────────
    #  FALLBACK: SMART STATIC RECOMMENDATIONS
    # ─────────────────────────────────────────────────────────

    def _get_fallback_recommendations(self, user_prefs: dict) -> dict:
        """
        Intelligent static fallback: scores destinations by style match,
        handles currency conversion, always returns within + beyond-budget options.
        """
        budget_raw = float(user_prefs.get('budget', 50000))
        currency = user_prefs.get('currency', 'INR').upper()
        styles = [s.lower() for s in user_prefs.get('destination_styles', [])]
        from_loc = user_prefs.get('from_location', 'India')
        num_days = int(user_prefs.get('num_days', 5))
        travel_scope = user_prefs.get('travel_scope', 'within_country')

        # Convert user budget to INR for comparison (DB is in INR)
        inr_rate = CURRENCY_TO_INR.get(currency, 84)
        budget_inr = budget_raw * inr_rate
        display_rate = 1.0 / inr_rate  # INR → user currency

        # Filter pool by scope
        if travel_scope == 'within_country':
            pool = [d for d in ALL_DESTINATIONS if not d.get('international', False)]
        else:
            # User selected International — strictly show international destinations
            pool_intl = [d for d in ALL_DESTINATIONS if d.get('international', True)]
            pool = [d for d in pool_intl if d.get('international', False)]
            if not pool:
                pool = list(ALL_DESTINATIONS)

        # Style scoring — uses STYLE_ALIASES for robust matching
        def style_score(dest):
            if not styles:
                return 1
            d_styles = {s.lower().strip() for s in dest.get('styles', [])}
            score = 0
            for user_style in styles:
                expanded = _normalize_style(user_style)
                if expanded & d_styles:
                    score += 2
                else:
                    user_words = set(user_style.split())
                    for ds in d_styles:
                        ds_words = set(ds.split())
                        common = (user_words & ds_words) - {'&', 'and', 'the'}
                        if common:
                            score += 1
                            break
            return score

        scored = [(style_score(d), d) for d in pool]
        
        # Scale cost by number of days (base is 5-day trip) and travel medium
        medium = user_prefs.get('travel_medium', 'any')
        medium_multiplier = 0.60
        if medium == 'bus': medium_multiplier = 0.50
        elif medium == 'train': medium_multiplier = 0.55
        elif medium == 'flight': medium_multiplier = 0.85
        elif medium == 'travel_agency': medium_multiplier = 1.30

        def compute_cost(dest):
            base = dest['base_cost']
            cpd = dest['cost_per_day']
            adjusted = base + (num_days - 5) * cpd
            raw_cost = max(adjusted, cpd * num_days)
            return raw_cost * medium_multiplier

        # Prepare candidates with scores and costs
        candidates = []
        for score, dest in scored:
            cost = compute_cost(dest)
            candidates.append({
                'score': score,
                'dest': dest,
                'cost': cost
            })

        # Shuffle candidates to ensure variety within same score levels
        random.shuffle(candidates)
        
        # Sort by score DESC primarily
        candidates.sort(key=lambda x: -x['score'])

        over_budget_threshold = budget_inr * 1.5

        def make_dest_copy(dest, cost_inr):
            d = dict(dest)
            display_cost = round(cost_inr * display_rate)
            if currency == 'INR':
                display_cost = int(cost_inr)
            d['estimated_total_cost'] = display_cost
            d['cost_per_day_display'] = round(dest['cost_per_day'] * display_rate) if currency != 'INR' else dest['cost_per_day']
            d['currency'] = currency
            d['best_for'] = [s.title() for s in dest.get('styles', [])[:4]]
            d['distance_from_start'] = dest.get('distance', 'Distance varies')
            return d

        within_budget = []
        over_budget = []

        # First pass: Get all viable candidates
        for cand in candidates:
            score = cand['score']
            dest = cand['dest']
            cost = cand['cost']
            
            if score <= 0 and styles:
                continue # Skip non-matching if styles were selected
            
            d = make_dest_copy(dest, cost)
            if cost <= budget_inr:
                d['within_budget'] = True
                d['over_budget_note'] = None
                if len(within_budget) < 6:
                    within_budget.append(d)
            elif cost <= over_budget_threshold:
                d['within_budget'] = False
                pct = int(((cost - budget_inr) / budget_inr) * 100)
                d['over_budget_note'] = f"~{pct}% over budget — but the experience is absolutely worth it!"
                if len(over_budget) < 3:
                    over_budget.append(d)

        # Emergency: if no within-budget matches, relax style filter (ignore score > 0)
        if not within_budget:
            for cand in candidates:
                dest = cand['dest']
                cost = cand['cost']
                if cost <= budget_inr and len(within_budget) < 4:
                    d = make_dest_copy(dest, cost)
                    d['within_budget'] = True
                    d['over_budget_note'] = None
                    within_budget.append(d)

        # Ensure at least 2 over_budget suggestions
        if len(over_budget) < 2:
            used = {d['name'] for d in within_budget + over_budget}
            for cand in candidates:
                dest = cand['dest']
                cost = cand['cost']
                if dest['name'] in used: continue
                if budget_inr < cost <= over_budget_threshold:
                    d = make_dest_copy(dest, cost)
                    d['within_budget'] = False
                    pct = int(((cost - budget_inr) / budget_inr) * 100)
                    d['over_budget_note'] = f"~{pct}% over budget — but the experience is absolutely worth it!"
                    over_budget.append(d)
                    if len(over_budget) >= 3: break


        result = within_budget + over_budget
        for i, d in enumerate(result, 1):
            d['id'] = i

        styles_display = ', '.join(styles).title() if styles else 'various destinations'
        api_note = ' (Add your free Gemini API key in .env for real-time AI-powered recommendations — visit aistudio.google.com/app/apikey)' if not self.available else ''

        return {
            'recommendations': result,
            'ai_summary': (
                f"Showing {len(result)} curated destinations for {prefs_display(user_prefs)} matching {styles_display}. "
                f"{len(within_budget)} destinations fit your {currency} {budget_raw:,.0f} budget, "
                f"and {len(over_budget)} premium options are included as aspirational picks.{api_note}"
            ),
        }

    # ─────────────────────────────────────────────────────────
    #  FALLBACK: DESTINATION DETAILS
    # ─────────────────────────────────────────────────────────

    def _get_fallback_destination_details(self, destination_name: str, user_prefs: dict) -> dict:
        """Return basic static details for any destination."""
        currency = user_prefs.get('currency', 'INR')
        from_loc = user_prefs.get('from_location', 'India')
        num_days = user_prefs.get('num_days', 5)
        budget = user_prefs.get('budget', 50000)

        return {
            "name": destination_name,
            "full_location": destination_name,
            "distance_from_start": f"From {from_loc}",
            "overview": (
                f"{destination_name} is a wonderful travel destination with rich culture, "
                f"scenic landscapes, and memorable experiences. Perfect for a {num_days}-day trip "
                f"from {from_loc}. Add your Gemini API key to get AI-powered detailed information."
            ),
            "famous_for": ["Scenic beauty", "Local culture", "Unique cuisine", "Memorable experiences"],
            "best_season": "October to March (pleasant weather for most Indian destinations)",
            "tourist_spots": [
                {"name": "Main Attraction", "description": "The most popular landmark", "entry_fee": f"{currency} 50-500"},
                {"name": "Local Market", "description": "Shop for local handicrafts and street food", "entry_fee": "Free"},
            ],
            "food_spots": [
                {"name": "Local Dhaba", "specialty": "Regional cuisine", "avg_cost": f"{currency} 100-300 per person"},
            ],
            "travel_options": [
                {"mode": "Train", "duration": "Varies", "cost": "Varies", "from": from_loc},
                {"mode": "Flight", "duration": "Varies", "cost": "Varies", "from": from_loc},
            ],
            "accommodation": [
                {"type": "Budget", "name": "Local guesthouses", "cost_per_night": f"{currency} 500-1500"},
                {"type": "Mid-range", "name": "Business hotels", "cost_per_night": f"{currency} 2000-5000"},
            ],
            "events_festivals": self._get_static_festivals(destination_name),
            "cost_breakdown": {
                "travel_to_destination": f"{currency} varies",
                "accommodation_total": f"{currency} for {num_days} nights",
                "food_total": f"{currency} for {num_days} days",
                "sightseeing_total": f"{currency} varies",
                "miscellaneous": f"{currency} 2000-5000",
                "grand_total": f"{currency} {int(budget)}",
            },
            "travel_tips": [
                "Book tickets in advance, especially during peak season (October-March)",
                "Carry cash as not all places accept cards",
                "Respect local customs and dress modestly at religious sites",
                "Try local street food but ensure it is freshly cooked",
            ],
            "local_transport": "Auto-rickshaws, local buses, and app-based cabs (Ola/Uber) are usually available",
        }

    # ─────────────────────────────────────────────────────────
    #  STATIC FESTIVAL DATABASE (used by fallback)
    # ─────────────────────────────────────────────────────────

    def _get_static_festivals(self, destination_name: str) -> list:
        """Return real festivals/events for a destination from a static DB."""
        FESTIVALS_DB = {
            "goa": [
                {"name": "Carnival of Goa", "month": "February", "description": "A 3-day pre-Lenten celebration with colorful parades, street dancing, live music, and elaborate floats through Panaji. King Momo rules the festivities with revelry and feasting."},
                {"name": "Sunburn Festival", "month": "December", "description": "Asia's largest electronic dance music festival held on the beaches of Goa, featuring world-class DJs, stunning light shows, and beach parties lasting three days."},
                {"name": "Shigmo Festival", "month": "March", "description": "Goa's version of Holi — a grand spring festival with traditional folk dances, elaborate street processions, colorful floats, and vibrant cultural performances."},
                {"name": "Feast of St. Francis Xavier", "month": "December (3rd)", "description": "A major Catholic pilgrimage at Old Goa's Basilica of Bom Jesus, venerating the patron saint's relics with Masses, processions, and a large fair."},
            ],
            "manali": [
                {"name": "Winter Carnival", "month": "January", "description": "A week-long winter celebration featuring skiing competitions, folk dances, music performances, beauty pageants, and bonfire nights against the backdrop of snow-clad Himalayas."},
                {"name": "Hadimba Devi Festival (Dhungri Mela)", "month": "May", "description": "A vibrant 3-day cultural fair at the Hadimba Temple with traditional Kullu folk dances, local handicraft stalls, and rituals honoring Goddess Hadimba."},
                {"name": "Dussehra (Kullu Dussehra)", "month": "October", "description": "Unlike the rest of India, Kullu Dussehra BEGINS on Vijayadashami and lasts 7 days. Over 200 village deities are brought in grand processions to Dhalpur Maidan."},
            ],
            "kerala": [
                {"name": "Onam", "month": "August–September", "description": "Kerala's grandest harvest festival spanning 10 days — featuring spectacular Pookalam (flower rangoli), Onasadya (26-course feast on banana leaves), Vallam Kali (snake boat races), and Pulikali (tiger dance)."},
                {"name": "Nehru Trophy Boat Race", "month": "August (2nd Saturday)", "description": "The most famous snake boat race in India, held on Punnamada Lake in Alleppey. Over 100-foot-long Chundan Vallams race to the deafening cheers of lakhs of spectators."},
                {"name": "Thrissur Pooram", "month": "April–May", "description": "A spectacular temple festival in Thrissur featuring a grand procession of 30+ caparisoned elephants, traditional Panchavadyam percussion orchestra, and a breathtaking fireworks display at dawn."},
                {"name": "Theyyam Season", "month": "November–March", "description": "Ancient ritualistic dance form performed in temples across North Kerala. Dancers adorned with elaborate costumes and face paint become living gods in a trance-like devotional performance."},
            ],
            "rajasthan": [
                {"name": "Pushkar Camel Fair", "month": "November", "description": "The world's largest camel fair in Pushkar — thousands of camels traded, decorated, and raced. Includes folk performances, hot air balloon rides, and a surreal moonlit desert atmosphere."},
                {"name": "Desert Festival Jaisalmer", "month": "February", "description": "A 3-day extravaganza on Sam Sand Dunes featuring camel races, turban-tying contests, folk music, puppet shows, and a mesmerizing Mr. Desert competition."},
                {"name": "Gangaur Festival", "month": "March–April", "description": "A vibrant Rajasthani festival celebrating Goddess Gauri (Parvati). Women dress in colorful attire, carry decorated idols through processions, and pray for marital bliss."},
                {"name": "Mewar Festival (Udaipur)", "month": "March–April", "description": "Udaipur's cultural extravaganza welcoming spring with traditional songs, dances, stunning processions to Lake Pichola, and fireworks lighting up the City of Lakes."},
            ],
            "jaisalmer": [
                {"name": "Desert Festival", "month": "February", "description": "A 3-day festival on Sam Sand Dunes with folk music, camel races, turban-tying contests, and Mr. Desert competition. The golden fort glows as the backdrop for cultural performances."},
                {"name": "Gangaur Festival", "month": "March–April", "description": "Women carry beautifully decorated clay idols of Goddess Gauri through the narrow lanes of Jaisalmer Fort in colorful processions with folk songs."},
                {"name": "Marwar Festival", "month": "October", "description": "A celebration of Rajasthani folk heroes through music and dance. Performances of Maand (classical singing), folk dances, and puppet shows bring Marwar's heritage alive."},
            ],
            "ladakh": [
                {"name": "Hemis Festival", "month": "June–July", "description": "Ladakh's biggest monastery festival at Hemis Gompa celebrating Guru Padmasambhava's birthday. Monks perform sacred Cham dances with colorful masks and elaborate brocade costumes."},
                {"name": "Ladakh Festival", "month": "September", "description": "A 15-day government-organized cultural showcase featuring traditional archery, polo matches, masked dances, yak races, and Ladakhi folk performances."},
                {"name": "Losar (Ladakhi New Year)", "month": "December–January", "description": "The Ladakhi New Year celebration with Buddhist rituals, family gatherings, traditional food like Khapse (fried pastry), and two weeks of merrymaking."},
            ],
            "varanasi": [
                {"name": "Dev Deepawali", "month": "November", "description": "The 'Festival of Lights of the Gods' — over a million earthen lamps (diyas) light up the 80+ ghats of the Ganges. A breathtaking spectacle with fireworks, aarti, and music on full moon night."},
                {"name": "Ganga Mahotsav", "month": "November", "description": "A 5-day cultural festival coinciding with Dev Deepawali featuring classical music, dance performances, wrestling bouts, and the spectacular illumination of all ghats."},
                {"name": "Maha Shivaratri", "month": "February–March", "description": "One of the holiest nights at the Kashi Vishwanath Temple. Thousands of devotees throng the temple for night-long prayers, abhishekam, and the sacred procession (Baraat) of Lord Shiva."},
                {"name": "Holi (Rangbhari Ekadashi)", "month": "March", "description": "Varanasi's unique Holi at Manikarnika Ghat blends colors with spirituality. The entire city erupts in color, thandai (bhang drink), and folk music at every ghat."},
            ],
            "rishikesh": [
                {"name": "International Yoga Festival", "month": "March (1st week)", "description": "A 7-day global yoga gathering at Parmarth Niketan ashram attracting thousands of yoga practitioners. Features sessions by world-renowned yogis, meditation, and Ganga Aarti."},
                {"name": "Ganga Dussehra", "month": "May–June", "description": "Celebrating the descent of River Ganga to Earth. Thousands float diyas on the Ganges with special puja ceremonies and cultural processions along the riverbanks."},
                {"name": "Maha Shivaratri", "month": "February–March", "description": "A grand celebration at Ram Jhula and Lakshman Jhula with all-night Shiva chanting, special aarti, and spiritual gatherings at riverside temples."},
            ],
            "andaman": [
                {"name": "Island Tourism Festival", "month": "January", "description": "A 10-day cultural fiesta in Port Blair featuring dance shows from mainland India and Andaman's indigenous tribes, adventure sport exhibitions, and local handicraft bazaars."},
                {"name": "Beach Festival", "month": "April–May", "description": "Water sports competitions, sandcastle building, beach volleyball, and musical performances along the pristine beaches of the Andaman Islands."},
                {"name": "Subhash Mela", "month": "January (23rd)", "description": "Commemorating Netaji Subhash Chandra Bose's birth anniversary with a grand fair at Port Blair featuring cultural shows, exhibitions, and patriotic events."},
            ],
            "hampi": [
                {"name": "Hampi Utsav (Vijaya Vittala Festival)", "month": "November", "description": "A grand 3-day cultural extravaganza among the ruins of Vijayanagara Empire. Includes classical dance, music concerts, puppet shows, processions with decorated elephants, and a fireworks finale."},
                {"name": "Virupaksha Car Festival", "month": "February", "description": "A massive chariot procession at the Virupaksha Temple — the towering wooden chariot is pulled through Hampi's main bazaar street by hundreds of devotees."},
                {"name": "Purandaradasa Festival", "month": "January–February", "description": "A 3-day Carnatic music festival commemorating the legendary musician Purandaradasa with concerts by top musicians amid Hampi's ancient temple setting."},
            ],
            "coorg": [
                {"name": "Kaveri Sankramana", "month": "October", "description": "The sacred festival marking the rise of River Kaveri at Talakaveri. Thousands gather at the spring's origin to witness the miraculous gush of water at an auspicious moment."},
                {"name": "Kodava Hockey Festival", "month": "March–April", "description": "The largest hockey tournament in Asia, organized in Kodagu. A major cultural gathering for the Kodava community with folk performances and traditional feasts."},
                {"name": "Blossom Flower Show", "month": "April", "description": "A vibrant display of Coorg's exotic flowers, coffee blossoms, and ornamental plants at Raja's Seat garden with cultural programs and local food stalls."},
            ],
            "meghalaya": [
                {"name": "Shad Suk Mynsiem (Weiking Dance)", "month": "April", "description": "The Khasi spring thanksgiving festival in Shillong — women dressed in golden silk and coral crowns perform graceful dances while men wear feathered headgear in a spectacular open-air celebration."},
                {"name": "Behdienkhlam", "month": "July", "description": "The largest Pnar (Jaintia) festival in Jowai — a dramatic rain-invocation ceremony where huge decorated wooden structures are dunked into a mud pit amid frenzied dancing."},
                {"name": "Nongkrem Dance Festival", "month": "November", "description": "A 5-day Khasi harvest festival near Shillong featuring sacred ritual dances at the Smit village, goat sacrifice, archery competitions, and a vibrant fair."},
            ],
            "mumbai": [
                {"name": "Ganesh Chaturthi (Ganapati Festival)", "month": "August–September", "description": "Mumbai's biggest festival — millions of devotees install Ganesh idols at home and in pandals for 10 days. The grand Visarjan procession goes on for 24+ hours with music, dance, and emotion."},
                {"name": "Kala Ghoda Arts Festival", "month": "February", "description": "A 9-day art extravaganza in South Mumbai's Kala Ghoda area with street art installations, literature events, music, dance performances, food stalls, and workshops."},
                {"name": "Navratri & Dandiya Nights", "month": "October", "description": "Mumbai comes alive with organized Dandiya Raas events in grounds across the city. Navratri garba nights at venues like NSCI Dome attract lakhs of dancers."},
                {"name": "Banganga Festival", "month": "January", "description": "A 2-day classical music festival at the ancient Banganga Tank in Malabar Hill — top Hindustani musicians perform against the backdrop of this 1000-year-old heritage site."},
            ],
            "amritsar": [
                {"name": "Baisakhi", "month": "April (13th)", "description": "The Sikh harvest New Year celebrated grandly at the Golden Temple with special prayers (Akhand Path), vibrant Bhangra, processions (Nagar Kirtan), and a spectacular fireworks display."},
                {"name": "Guru Nanak Jayanti", "month": "November", "description": "The birth anniversary of Guru Nanak celebrated with a 48-hour Akhand Path, serene Prabhat Pheris (dawn processions), and massive community langars serving millions."},
                {"name": "Wagah Border Retreat Ceremony", "month": "Daily (year-round)", "description": "Not a festival per se, but an electrifying daily ceremony at the India-Pakistan border with high-stepping soldiers, patriotic fervor, and thousands of cheering spectators."},
            ],
            "bali": [
                {"name": "Nyepi (Day of Silence)", "month": "March", "description": "Bali's unique Hindu New Year — the entire island shuts down for 24 hours. No lights, no travel, no activity. The night before features Ogoh-Ogoh parade with giant demon effigies."},
                {"name": "Galungan & Kuningan", "month": "Varies (210-day cycle)", "description": "A 10-day Balinese Hindu celebration of good over evil. Temples are decorated with bamboo Penjor poles, families offer prayers, and traditional Barong dances fill the streets."},
                {"name": "Ubud Writers & Readers Festival", "month": "October", "description": "Southeast Asia's leading literary festival held in Ubud featuring international authors, workshops, cultural performances, and discussions amid rice paddies."},
            ],
            "thailand": [
                {"name": "Songkran (Thai New Year Water Festival)", "month": "April (13–15)", "description": "The world-famous Thai water festival — the entire country erupts in a massive water fight for 3 days. Traditional rituals include pouring water on elders' hands for blessings."},
                {"name": "Loy Krathong", "month": "November", "description": "The enchanting 'Festival of Lights' where thousands of candle-lit banana leaf boats (krathongs) are released on rivers. In Chiang Mai, sky lanterns (Yi Peng) light up the night sky."},
                {"name": "Full Moon Party (Koh Phangan)", "month": "Monthly", "description": "The legendary monthly beach party on Haad Rin Beach with 20,000+ revelers, neon body paint, fire dancers, and DJs playing until dawn."},
            ],
            "dubai": [
                {"name": "Dubai Shopping Festival (DSF)", "month": "December–January", "description": "A month-long mega shopping event with massive discounts, daily raffles (win luxury cars and gold!), global village, fireworks, and entertainment shows across the city."},
                {"name": "Dubai Food Festival", "month": "February–March", "description": "A 23-day culinary celebration with pop-up restaurants, food trucks, celebrity chef events, and the famous 'Beach Canteen' along Jumeirah Beach."},
                {"name": "Dubai International Film Festival", "month": "December", "description": "A premier regional film festival showcasing Arab and international cinema with red carpet premieres, filmmaker talks, and outdoor screenings under the stars."},
            ],
            "nepal": [
                {"name": "Dashain (Durga Puja)", "month": "October", "description": "Nepal's biggest and longest festival lasting 15 days. Families gather for elaborate feasts, kite flying, animal sacrifices to Goddess Durga, and receiving tika (sacred vermillion) from elders."},
                {"name": "Holi (Festival of Colors)", "month": "March", "description": "Celebrated with wild enthusiasm in Kathmandu's Durbar Square — water balloons, colored powder, music, and dancing fill the streets for two days."},
                {"name": "Indra Jatra", "month": "September", "description": "A spectacular 8-day festival in Kathmandu with the chariot procession of the Living Goddess (Kumari), masked dances, and traditional Newari feasting."},
            ],
            "singapore": [
                {"name": "Chinese New Year (Chinatown)", "month": "January–February", "description": "Spectacular celebrations in Chinatown with elaborate street decorations, lion dances, Chingay parade (Asia's largest street performance), and a massive River Hongbao festival."},
                {"name": "National Day (NDP)", "month": "August (9th)", "description": "Singapore's birthday celebration at Marina Bay with a jaw-dropping military parade, iconic Red Lions sky dive, NDP songs, and Southeast Asia's most impressive fireworks display."},
                {"name": "Deepavali (Little India)", "month": "October–November", "description": "Little India transforms into a dazzling corridor of lights and decorations. Night bazaars, cultural performances, and the entire Serangoon Road glowing with festive illuminations."},
            ],
            "ooty": [
                {"name": "Ooty Flower Show", "month": "May", "description": "A spectacular 3-day exhibition at the Botanical Gardens showcasing rare and exotic flowers, roses, dahlias, and ornamental plants grown in the Nilgiris. Attracts over 1 lakh visitors."},
                {"name": "Tea and Tourism Festival", "month": "December–January", "description": "Celebrating Ooty's tea heritage with tea-tasting sessions, estate tours, cultural performances, and nature walks through the rolling tea plantations of the Nilgiris."},
                {"name": "Summer Festival", "month": "May–June", "description": "A cultural fiesta featuring boat races on Ooty Lake, horticulture exhibitions, tribal dance performances, and night bazaars in the cool Nilgiri summer weather."},
            ],
            "kodaikanal": [
                {"name": "Summer Festival", "month": "May", "description": "A 3-day celebration organized by the Tamil Nadu Tourism Department with flower shows, dog shows, cultural concerts by top artists, and boat races on Kodai Lake."},
                {"name": "Pongal Celebrations", "month": "January", "description": "The Tamil harvest festival celebrated with traditional rituals, Jallikattu references, Pongal cooking in open pots, folk dances, and kolam art competitions."},
            ],
            "pondicherry": [
                {"name": "Bastille Day", "month": "July (14th)", "description": "A unique French heritage celebration in Pondicherry — the only place in India that celebrates France's national day with parades, French tricolor decorations, and cultural events in the French Quarter."},
                {"name": "International Yoga Festival", "month": "January", "description": "A 7-day gathering at Sri Aurobindo Ashram and Auroville with yoga workshops, meditation sessions, and spiritual talks by renowned practitioners from around the world."},
                {"name": "Masquerade Festival", "month": "February–March", "description": "Pondicherry's Mardi Gras-inspired carnival with masked processions, colorful costumes, float parades through the French Quarter, and live music performances on the promenade."},
            ],
            "spiti": [
                {"name": "Losar (Spitian New Year)", "month": "January", "description": "Spiti's Buddhist New Year celebration with devil dances at Ki and Tabo monasteries, special prayers, feasting on traditional dishes like Thukpa, and the entire valley decorated with prayer flags."},
                {"name": "Cham Dance Festival (at Ki Monastery)", "month": "June–July", "description": "Sacred masked dances performed by monks at the spectacular Ki Monastery depicting the triumph of good over evil. Attended by villagers from across the Spiti Valley."},
                {"name": "Fagli Festival", "month": "February", "description": "A colorful carnival-like winter festival with masked performances, folk singing, and community feasting — Spiti's way of chasing away winter evil spirits."},
            ],
            "darjeeling": [
                {"name": "Darjeeling Carnival", "month": "November–December", "description": "A week-long winter celebration with parades, live bands, beauty pageants, cultural shows, food stalls, and activities along the mall road and Chowrasta area."},
                {"name": "Losar (Tibetan New Year)", "month": "February–March", "description": "Celebrated by the Tibetan community in Darjeeling with monastery prayers, Cham dances, butter sculptures, and festive gatherings."},
                {"name": "Tea Tourism Festival", "month": "October", "description": "Celebrating Darjeeling's legendary tea heritage — tea estate tours, tea tasting, tea plucking experiences, and cultural programs in the misty tea gardens."},
            ],
        }

        name_lower = destination_name.lower()
        # Try to find matching key in the DB
        for key, festivals in FESTIVALS_DB.items():
            if key in name_lower or name_lower in key:
                return festivals

        # Partial matches (e.g., "Kerala Backwaters" → "kerala", "Rajasthan — Jaipur & Udaipur" → "rajasthan")
        for key, festivals in FESTIVALS_DB.items():
            if any(word in name_lower for word in key.split()):
                return festivals

        # Default generic but still real pan-Indian festivals
        return [
            {"name": "Diwali (Festival of Lights)", "month": "October–November", "description": "India's grandest festival celebrated with millions of oil lamps, fireworks, rangoli art, and sweets. Homes are cleaned and decorated, and families gather for Lakshmi Puja."},
            {"name": "Holi (Festival of Colors)", "month": "March", "description": "A joyous spring celebration where people drench each other in colored powder and water. Music, dance, and traditional drinks like thandai mark this festival of love and forgiveness."},
            {"name": "Makar Sankranti / Pongal", "month": "January (14th)", "description": "A harvest festival celebrated across India with kite flying (North) or Pongal cooking (South). Marks the sun's transition into Capricorn and the end of winter."},
        ]


def prefs_display(prefs):
    """Helper for readable user name in summaries."""
    return prefs.get('name', 'you')
