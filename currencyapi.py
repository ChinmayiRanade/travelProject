import requests
import os


API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
BASE_URL = "https://api.exchangerate.host/convert"

CITY_TO_CURRENCY = {
    "geneva": "CHF", "zurich": "CHF", "bern": "CHF", "basel": "CHF",
    "paris": "EUR", "lyon": "EUR", "marseille": "EUR", "nice": "EUR",
    "berlin": "EUR", "munich": "EUR", "hamburg": "EUR", "cologne": "EUR",
    "rome": "EUR", "milan": "EUR", "venice": "EUR", "florence": "EUR",
    "madrid": "EUR", "barcelona": "EUR", "valencia": "EUR", "seville": "EUR",
    "amsterdam": "EUR", "rotterdam": "EUR", "the hague": "EUR",
    "brussels": "EUR", "antwerp": "EUR", "ghent": "EUR",
    "vienna": "EUR", "salzburg": "EUR", "innsbruck": "EUR",
    "lisbon": "EUR", "porto": "EUR", "athens": "EUR", "thessaloniki": "EUR",
    "dublin": "EUR", "cork": "EUR", "helsinki": "EUR", "tampere": "EUR",
    "london": "GBP", "manchester": "GBP", "edinburgh": "GBP", "glasgow": "GBP",
    "birmingham": "GBP", "liverpool": "GBP", "bristol": "GBP", "leeds": "GBP",
    "tokyo": "JPY", "osaka": "JPY", "kyoto": "JPY", "nagoya": "JPY",
    "seoul": "KRW", "busan": "KRW", "incheon": "KRW", "daegu": "KRW",
    "singapore": "SGD", "hong kong": "HKD", "macau": "MOP",
    "bangkok": "THB", "phuket": "THB", "chiang mai": "THB",
    "kuala lumpur": "MYR", "penang": "MYR", "johor bahru": "MYR",
    "jakarta": "IDR", "bali": "IDR", "surabaya": "IDR",
    "manila": "PHP", "cebu": "PHP", "davao": "PHP",
    "mumbai": "INR", "delhi": "INR", "bangalore": "INR", "chennai": "INR",
    "kolkata": "INR", "hyderabad": "INR", "pune": "INR", "ahmedabad": "INR",
    "beijing": "CNY", "shanghai": "CNY", "guangzhou": "CNY", "shenzhen": "CNY",
    "taipei": "TWD", "kaohsiung": "TWD", "taichung": "TWD",
    "toronto": "CAD", "vancouver": "CAD", "montreal": "CAD", "calgary": "CAD",
    "ottawa": "CAD", "winnipeg": "CAD", "quebec city": "CAD",
    "mexico city": "MXN", "guadalajara": "MXN", "cancun": "MXN",
    "tijuana": "MXN", "puebla": "MXN", "playa del carmen": "MXN",
    "sao": "BRL", "rio": "BRL", "brasilia": "BRL", "salvador": "BRL",
    "fortaleza": "BRL", "belo": "BRL", "manaus": "BRL", "curitiba": "BRL",
    "buenos aires": "ARS", "rosario": "ARS", "mendoza": "ARS",
    "lima": "PEN", "cusco": "PEN", "arequipa": "PEN", "trujillo": "PEN",
    "santiago": "CLP", "valparaiso": "CLP", "concepcion": "CLP",
    "bogota": "COP", "medellin": "COP", "cartagena": "COP", "cali": "COP",
    "caracas": "VES", "maracaibo": "VES",
    "sydney": "AUD", "melbourne": "AUD", "brisbane": "AUD", "perth": "AUD",
    "adelaide": "AUD", "gold coast": "AUD", "canberra": "AUD", "darwin": "AUD",
    "auckland": "NZD", "christchurch": "NZD", "hamilton": "NZD",
    "suva": "FJD", "nadi": "FJD",
    "cape town": "ZAR", "johannesburg": "ZAR", "pretoria": "ZAR",
    "cairo": "EGP", "alexandria": "EGP", "giza": "EGP", "luxor": "EGP",
    "casablanca": "MAD", "rabat": "MAD", "marrakech": "MAD", "fez": "MAD",
    "lagos": "NGN", "abuja": "NGN", "kano": "NGN", "ibadan": "NGN",
    "nairobi": "KES", "mombasa": "KES", "kisumu": "KES",
    "addis ababa": "ETB", "dire dawa": "ETB",
    "dubai": "AED", "abu dhabi": "AED", "sharjah": "AED", "ajman": "AED",
    "riyadh": "SAR", "jeddah": "SAR", "mecca": "SAR", "medina": "SAR",
    "doha": "QAR", "al wakrah": "QAR", "al rayyan": "QAR",
    "kuwait city": "KWD", "hawalli": "KWD", "ahmadi": "KWD",
    "manama": "BHD", "riffa": "BHD", "muharraq": "BHD",
    "muscat": "OMR", "salalah": "OMR", "sohar": "OMR",
    "tel aviv": "ILS", "jerusalem": "ILS", "haifa": "ILS", "beersheba": "ILS",
    "istanbul": "TRY", "ankara": "TRY", "izmir": "TRY", "bursa": "TRY",
    "tehran": "IRR", "mashhad": "IRR", "isfahan": "IRR", "karaj": "IRR",
    "reykjavik": "ISK", "akureyri": "ISK", "keflavik": "ISK",
    "oslo": "NOK", "bergen": "NOK", "trondheim": "NOK", "stavanger": "NOK",
    "stockholm": "SEK", "gothenburg": "SEK", "malmo": "SEK", "uppsala": "SEK",
    "copenhagen": "DKK", "aarhus": "DKK", "odense": "DKK", "aalborg": "DKK",
    "prague": "CZK", "brno": "CZK", "ostrava": "CZK", "plzen": "CZK",
    "warsaw": "PLN", "krakow": "PLN", "lodz": "PLN", "wroclaw": "PLN",
    "budapest": "HUF", "debrecen": "HUF", "szeged": "HUF", "miskolc": "HUF",
    "bucharest": "RON", "timisoara": "RON", "iasi": "RON",
    "sofia": "BGN", "plovdiv": "BGN", "varna": "BGN", "burgas": "BGN",
    "zagreb": "HRK", "split": "HRK", "rijeka": "HRK", "osijek": "HRK",
    "belgrade": "RSD", "novi sad": "RSD", "nis": "RSD", "kragujevac": "RSD",
    "moscow": "RUB", "saint petersburg": "RUB",
    "kiev": "UAH", "kharkiv": "UAH", "odessa": "UAH", "dnipro": "UAH",
}


def get_rate_from_usd_to(currency: str) -> str:
    """Return the conversion rate."""
    params = {
        "access_key": API_KEY,  # API key as shown in the sample
        "from": "USD",
        "to": currency,
        "amount": 1
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check if the API returned success
        if not data.get("success"):
            return "Rate unavailable"

        rate = data["result"]
        return f"1 USD = {rate:.2f} {currency}"

    except requests.RequestException:
        return "Rate unavailable"


def get_rate_for_city(city: str) -> str:
    """Get USD to local currency rate for a given city."""
    city_lower = city.lower().strip()

    if city_lower not in CITY_TO_CURRENCY:
        return f"Currency information not available for {city}"

    currency = CITY_TO_CURRENCY[city_lower]
    return get_rate_from_usd_to(currency)


def get_city_currency(city: str) -> str:
    """Get the currency code for a given city."""
    city_lower = city.lower().strip()
    return CITY_TO_CURRENCY.get(city_lower, "Unknown")
