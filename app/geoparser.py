"""
GEO INTEL — geoparser.py
Ekstrak lokasi dari teks artikel dan tentukan koordinat
"""
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROVINCES, CITIES, INCIDENT_KEYWORDS, INCIDENT_TYPES

# ── Build lookup cepat ────────────────────────────────────────────────────────
_CITY_LOWER    = {k.lower(): v | {"name": k} for k, v in CITIES.items()}
_PROVINCE_LOWER= {k.lower(): v | {"name": k} for k, v in PROVINCES.items()}

# Alias tambahan yang sering muncul di berita
LOCATION_ALIASES = {
    "jakarta":          "Jakarta",
    "ibu kota":         "Jakarta",
    "dki":              "Jakarta",
    "indonesia":        "Jakarta",   # fallback ke pusat jika hanya sebut Indonesia
    "indonesian":       "Jakarta",
    "jabar":            "Jawa Barat",
    "jateng":           "Jawa Tengah",
    "jatim":            "Jawa Timur",
    "diy":              "DI Yogyakarta",
    "jogja":            "DI Yogyakarta",
    "yogya":            "DI Yogyakarta",
    "sumut":            "Sumatera Utara",
    "sumsel":           "Sumatera Selatan",
    "sumbar":           "Sumatera Barat",
    "sulsel":           "Sulawesi Selatan",
    "sulteng":          "Sulawesi Tengah",
    "sulut":            "Sulawesi Utara",
    "sultra":           "Sulawesi Tenggara",
    "kalbar":           "Kalimantan Barat",
    "kalteng":          "Kalimantan Tengah",
    "kalsel":           "Kalimantan Selatan",
    "kaltim":           "Kalimantan Timur",
    "kalut":            "Kalimantan Utara",
    "ntb":              "Nusa Tenggara Barat",
    "ntt":              "Nusa Tenggara Timur",
    "babel":            "Kepulauan Bangka Belitung",
    "kepri":            "Kepulauan Riau",
    "malut":            "Maluku Utara",
    "papua barat":      "Papua Barat",
    "bali":             "Bali",
    "aceh":             "Aceh",
    "riau":             "Riau",
    "jambi":            "Jambi",
    "bengkulu":         "Bengkulu",
    "lampung":          "Lampung",
    "gorontalo":        "Gorontalo",
    "maluku":           "Maluku",
    "papua":            "Papua",
    # Nama yang sering muncul di berita internasional
    "west java":        "Jawa Barat",
    "east java":        "Jawa Timur",
    "central java":     "Jawa Tengah",
    "north sumatra":    "Sumatera Utara",
    "west sumatra":     "Sumatera Barat",
    "south sumatra":    "Sumatera Selatan",
    "north sulawesi":   "Sulawesi Utara",
    "south sulawesi":   "Sulawesi Selatan",
    "west kalimantan":  "Kalimantan Barat",
    "east kalimantan":  "Kalimantan Timur",
    "west papua":       "Papua Barat",
    "bandung":          "Bandung",
    "bekasi":           "Bekasi",
    "bogor":            "Bogor",
    "tangerang":        "Tangerang",
    "yogyakarta":       "DI Yogyakarta",
    "sulawesi":         "Sulawesi Selatan",
    "kalimantan":       "Kalimantan Timur",
    "sumatra":          "Sumatera Utara",
    "sumatera":         "Sumatera Utara",
    "borneo":           "Kalimantan Timur",
}

def extract_locations(text: str) -> list:
    """
    Ekstrak semua lokasi yang disebut dalam teks.
    Return: list of {name, lat, lon, province, type}
    """
    if not text:
        return []

    text_lower = text.lower()
    found = {}

    # 1. Cek alias dulu (singkatan provinsi)
    for alias, canonical in LOCATION_ALIASES.items():
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, text_lower):
            if canonical in CITIES:
                info = CITIES[canonical]
                found[canonical] = {
                    "name":     canonical,
                    "lat":      info["lat"],
                    "lon":      info["lon"],
                    "province": info.get("province", canonical),
                    "type":     "city",
                }
            elif canonical in PROVINCES:
                info = PROVINCES[canonical]
                found[canonical] = {
                    "name":     canonical,
                    "lat":      info["lat"],
                    "lon":      info["lon"],
                    "province": canonical,
                    "type":     "province",
                }

    # 2. Cek nama kota
    for city_lower, info in _CITY_LOWER.items():
        pattern = r'\b' + re.escape(city_lower) + r'\b'
        if re.search(pattern, text_lower):
            name = info["name"]
            if name not in found:
                found[name] = {
                    "name":     name,
                    "lat":      info["lat"],
                    "lon":      info["lon"],
                    "province": info.get("province", ""),
                    "type":     "city",
                }

    # 3. Cek nama provinsi
    for prov_lower, info in _PROVINCE_LOWER.items():
        pattern = r'\b' + re.escape(prov_lower) + r'\b'
        if re.search(pattern, text_lower):
            name = info["name"]
            if name not in found:
                found[name] = {
                    "name":     name,
                    "lat":      info["lat"],
                    "lon":      info["lon"],
                    "province": name,
                    "type":     "province",
                }

    return list(found.values())


def classify_incident(text: str) -> str:
    """
    Tentukan tipe insiden dari teks.
    Return: kode tipe (BENCANA, KONFLIK, KRIMINAL, POLITIK, EKONOMI, KESEHATAN, LAINNYA)
    """
    text_lower = text.lower()
    scores = {}
    for inc_type, keywords in INCIDENT_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw.lower() in text_lower)
        if hits > 0:
            scores[inc_type] = hits

    if not scores:
        return "LAINNYA"
    return max(scores, key=scores.get)


def compute_severity(text: str, inc_type: str) -> float:
    """
    Hitung severity 0-100 berdasarkan konten artikel.
    """
    text_lower = text.lower()
    score = 20.0  # baseline

    # Keyword darurat
    URGENCY_HIGH = [
        "korban jiwa", "meninggal", "tewas", "kritis", "darurat",
        "evakuasi", "bencana besar", "massal", "ratusan", "ribuan",
        "dead", "killed", "emergency", "critical", "mass",
    ]
    URGENCY_MED = [
        "korban luka", "terdampak", "rusak", "mengungsi",
        "injured", "damaged", "displaced", "affected",
    ]

    high_hits = sum(1 for kw in URGENCY_HIGH if kw in text_lower)
    med_hits  = sum(1 for kw in URGENCY_MED  if kw in text_lower)

    score += high_hits * 15
    score += med_hits  * 8

    # Angka korban
    numbers = re.findall(r'(\d+)\s*(orang|korban|jiwa|warga|rumah|desa|hektar)', text_lower)
    for num_str, _ in numbers:
        num = int(num_str)
        if num >= 100:
            score += 20
        elif num >= 10:
            score += 10
        elif num >= 1:
            score += 5

    # Bobot per tipe
    TYPE_WEIGHTS = {
        "BENCANA":   1.1,
        "KONFLIK":   1.0,
        "KRIMINAL":  0.9,
        "POLITIK":   0.7,
        "EKONOMI":   0.8,
        "KESEHATAN": 1.0,
        "LAINNYA":   0.6,
    }
    score *= TYPE_WEIGHTS.get(inc_type, 0.8)

    return round(min(score, 100), 1)


def parse_article_geo(article: dict) -> list:
    """
    Parse satu artikel → return list of geo incidents (satu artikel bisa
    menyebut beberapa lokasi).
    """
    title   = article.get("title", "")       or ""
    desc    = article.get("description", "") or ""
    content = article.get("content", "")     or ""
    # Gabungkan semua field teks yang tersedia
    text    = " ".join([title, desc, content]).strip()

    locations = extract_locations(text)
    inc_type = classify_incident(text)
    severity = compute_severity(text, inc_type)

    # Jika tidak ada lokasi spesifik tapi ada keyword insiden → fallback Indonesia
    if not locations and inc_type != "LAINNYA" and severity >= 20:
        locations = [{
            "name":     "Indonesia",
            "lat":      -2.5,
            "lon":      118.0,
            "province": "Nasional",
            "type":     "country",
        }]
    elif not locations:
        return []

    incidents = []
    for loc in locations[:3]:  # max 3 lokasi per artikel
        incidents.append({
            "title":       title,
            "description": desc,
            "source":      article.get("source",""),
            "url":         article.get("url",""),
            "published_at":article.get("publishedAt","") or article.get("published_at",""),
            "location":    loc["name"],
            "province":    loc["province"],
            "lat":         loc["lat"],
            "lon":         loc["lon"],
            "loc_type":    loc["type"],
            "inc_type":    inc_type,
            "severity":    severity,
        })
    return incidents
