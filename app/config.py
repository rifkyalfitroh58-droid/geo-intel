"""
GEO INTEL — config.py
Konfigurasi + database koordinat lengkap Indonesia
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except ImportError:
    pass

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DB_PATH     = os.path.join(
    os.getenv("STREAMLIT_DATA_DIR", "/tmp"),
    "geo_intel.db"
)

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "isi_api_key_kamu_di_sini")

# ── Kategori insiden ──────────────────────────────────────────────────────────
INCIDENT_TYPES = {
    "BENCANA":   {"label": "Bencana Alam",    "color": "#E74C3C", "icon": "🌊"},
    "KONFLIK":   {"label": "Konflik Sosial",   "color": "#E67E22", "icon": "⚔"},
    "KRIMINAL":  {"label": "Kriminal",         "color": "#9B59B6", "icon": "🔫"},
    "POLITIK":   {"label": "Politik",          "color": "#3498DB", "icon": "🏛"},
    "EKONOMI":   {"label": "Ekonomi",         "color": "#F39C12", "icon": "💰"},
    "KESEHATAN": {"label": "Kesehatan",        "color": "#2ECC71", "icon": "🏥"},
    "LAINNYA":   {"label": "Lainnya",          "color": "#95A5A6", "icon": "📌"},
}

# ── Severity level ────────────────────────────────────────────────────────────
SEVERITY_LEVELS = {
    "KRITIS": (75, 100, "#E74C3C"),
    "TINGGI": (50,  74, "#E67E22"),
    "SEDANG": (25,  49, "#F39C12"),
    "RENDAH": ( 0,  24, "#2ECC71"),
}

# ── Database koordinat provinsi Indonesia (34 provinsi) ───────────────────────
PROVINCES = {
    "Aceh":                    {"lat":  4.6951, "lon":  96.7494, "code": "ID-AC"},
    "Sumatera Utara":          {"lat":  2.1154, "lon":  99.5451, "code": "ID-SU"},
    "Sumatera Barat":          {"lat": -0.7399, "lon": 100.8000, "code": "ID-SB"},
    "Riau":                    {"lat":  0.2933, "lon": 101.7068, "code": "ID-RI"},
    "Kepulauan Riau":          {"lat":  3.9456, "lon": 108.1429, "code": "ID-KR"},
    "Jambi":                   {"lat": -1.6101, "lon": 103.6131, "code": "ID-JA"},
    "Sumatera Selatan":        {"lat": -3.3194, "lon": 103.9144, "code": "ID-SS"},
    "Kepulauan Bangka Belitung":{"lat":-2.7411, "lon": 106.4406, "code": "ID-BB"},
    "Bengkulu":                {"lat": -3.7928, "lon": 102.2608, "code": "ID-BE"},
    "Lampung":                 {"lat": -4.5586, "lon": 105.4068, "code": "ID-LA"},
    "DKI Jakarta":             {"lat": -6.2088, "lon": 106.8456, "code": "ID-JK"},
    "Jawa Barat":              {"lat": -6.9175, "lon": 107.6191, "code": "ID-JB"},
    "Banten":                  {"lat": -6.4058, "lon": 106.0640, "code": "ID-BT"},
    "Jawa Tengah":             {"lat": -7.1500, "lon": 110.1403, "code": "ID-JT"},
    "DI Yogyakarta":           {"lat": -7.7956, "lon": 110.3695, "code": "ID-YO"},
    "Jawa Timur":              {"lat": -7.5361, "lon": 112.2384, "code": "ID-JI"},
    "Bali":                    {"lat": -8.3405, "lon": 115.0920, "code": "ID-BA"},
    "Nusa Tenggara Barat":     {"lat": -8.6529, "lon": 117.3616, "code": "ID-NB"},
    "Nusa Tenggara Timur":     {"lat": -8.6574, "lon": 121.0794, "code": "ID-NT"},
    "Kalimantan Barat":        {"lat":  0.0000, "lon": 109.3333, "code": "ID-KB"},
    "Kalimantan Tengah":       {"lat": -1.6815, "lon": 113.3824, "code": "ID-KT"},
    "Kalimantan Selatan":      {"lat": -3.0926, "lon": 115.2838, "code": "ID-KS"},
    "Kalimantan Timur":        {"lat":  1.6407, "lon": 116.4194, "code": "ID-KI"},
    "Kalimantan Utara":        {"lat":  3.0731, "lon": 116.0413, "code": "ID-KU"},
    "Sulawesi Utara":          {"lat":  1.4931, "lon": 124.8413, "code": "ID-SA"},
    "Gorontalo":               {"lat":  0.5435, "lon": 123.0568, "code": "ID-GO"},
    "Sulawesi Tengah":         {"lat": -1.4300, "lon": 121.4456, "code": "ID-ST"},
    "Sulawesi Barat":          {"lat": -2.8442, "lon": 119.2321, "code": "ID-SR"},
    "Sulawesi Selatan":        {"lat": -3.6688, "lon": 119.9740, "code": "ID-SN"},
    "Sulawesi Tenggara":       {"lat": -4.1449, "lon": 122.1746, "code": "ID-SG"},
    "Maluku":                  {"lat": -3.2385, "lon": 130.1453, "code": "ID-MA"},
    "Maluku Utara":            {"lat":  1.5709, "lon": 127.8088, "code": "ID-MU"},
    "Papua Barat":             {"lat": -1.3361, "lon": 133.1747, "code": "ID-PB"},
    "Papua":                   {"lat": -4.2699, "lon": 138.0804, "code": "ID-PA"},
}

# ── Database kota besar Indonesia + koordinat ─────────────────────────────────
CITIES = {
    # Jawa
    "Jakarta":     {"lat": -6.2088, "lon": 106.8456, "province": "DKI Jakarta"},
    "Bandung":     {"lat": -6.9175, "lon": 107.6191, "province": "Jawa Barat"},
    "Surabaya":    {"lat": -7.2575, "lon": 112.7521, "province": "Jawa Timur"},
    "Semarang":    {"lat": -6.9932, "lon": 110.4203, "province": "Jawa Tengah"},
    "Yogyakarta":  {"lat": -7.7956, "lon": 110.3695, "province": "DI Yogyakarta"},
    "Malang":      {"lat": -7.9666, "lon": 112.6326, "province": "Jawa Timur"},
    "Bogor":       {"lat": -6.5971, "lon": 106.8060, "province": "Jawa Barat"},
    "Bekasi":      {"lat": -6.2383, "lon": 106.9756, "province": "Jawa Barat"},
    "Tangerang":   {"lat": -6.1783, "lon": 106.6319, "province": "Banten"},
    "Depok":       {"lat": -6.4025, "lon": 106.7942, "province": "Jawa Barat"},
    "Solo":        {"lat": -7.5755, "lon": 110.8243, "province": "Jawa Tengah"},
    "Serang":      {"lat": -6.1201, "lon": 106.1503, "province": "Banten"},
    # Sumatera
    "Medan":       {"lat":  3.5952, "lon":  98.6722, "province": "Sumatera Utara"},
    "Palembang":   {"lat": -2.9761, "lon": 104.7754, "province": "Sumatera Selatan"},
    "Pekanbaru":   {"lat":  0.5335, "lon": 101.4474, "province": "Riau"},
    "Batam":       {"lat":  1.0456, "lon": 104.0305, "province": "Kepulauan Riau"},
    "Padang":      {"lat": -0.9492, "lon": 100.3543, "province": "Sumatera Barat"},
    "Banda Aceh":  {"lat":  5.5483, "lon":  95.3238, "province": "Aceh"},
    "Lampung":     {"lat": -5.4294, "lon": 105.2610, "province": "Lampung"},
    "Bandar Lampung":{"lat":-5.4294,"lon": 105.2610, "province": "Lampung"},
    # Kalimantan
    "Pontianak":   {"lat": -0.0263, "lon": 109.3425, "province": "Kalimantan Barat"},
    "Samarinda":   {"lat": -0.5022, "lon": 117.1536, "province": "Kalimantan Timur"},
    "Balikpapan":  {"lat": -1.2379, "lon": 116.8529, "province": "Kalimantan Timur"},
    "Banjarmasin": {"lat": -3.3186, "lon": 114.5944, "province": "Kalimantan Selatan"},
    "Palangkaraya":{"lat": -2.2096, "lon": 113.9108, "province": "Kalimantan Tengah"},
    "Nusantara":   {"lat": -0.8500, "lon": 116.7200, "province": "Kalimantan Timur"},
    # Sulawesi
    "Makassar":    {"lat": -5.1477, "lon": 119.4327, "province": "Sulawesi Selatan"},
    "Manado":      {"lat":  1.4748, "lon": 124.8421, "province": "Sulawesi Utara"},
    "Palu":        {"lat": -0.9003, "lon": 119.8779, "province": "Sulawesi Tengah"},
    "Kendari":     {"lat": -3.9985, "lon": 122.5127, "province": "Sulawesi Tenggara"},
    "Gorontalo":   {"lat":  0.5435, "lon": 123.0568, "province": "Gorontalo"},
    # Bali & Nusa Tenggara
    "Denpasar":    {"lat": -8.6705, "lon": 115.2126, "province": "Bali"},
    "Mataram":     {"lat": -8.5833, "lon": 116.1167, "province": "Nusa Tenggara Barat"},
    "Kupang":      {"lat": -10.1772,"lon": 123.6070, "province": "Nusa Tenggara Timur"},
    # Maluku & Papua
    "Ambon":       {"lat": -3.6954, "lon": 128.1814, "province": "Maluku"},
    "Ternate":     {"lat":  0.7833, "lon": 127.3667, "province": "Maluku Utara"},
    "Jayapura":    {"lat": -2.5337, "lon": 140.7181, "province": "Papua"},
    "Sorong":      {"lat": -0.8833, "lon": 131.2500, "province": "Papua Barat"},
}

# ── Keyword kategori insiden ──────────────────────────────────────────────────
INCIDENT_KEYWORDS = {
    "BENCANA": [
        "gempa", "banjir", "longsor", "tsunami", "gunung meletus", "erupsi",
        "kebakaran hutan", "kekeringan", "angin puting beliung", "bencana",
        "korban", "evakuasi", "BNPB", "BPBD", "tanggap darurat",
        "earthquake", "flood", "landslide", "disaster", "eruption",
    ],
    "KONFLIK": [
        "bentrokan", "tawuran", "kerusuhan", "konflik", "demonstrasi",
        "unjuk rasa", "ricuh", "massa", "sweeping", "pengusiran",
        "riot", "clash", "protest", "unrest", "violence",
    ],
    "KRIMINAL": [
        "pembunuhan", "pencurian", "perampokan", "penipuan", "korupsi",
        "narkoba", "penangkapan", "tersangka", "kriminal", "kejahatan",
        "murder", "robbery", "fraud", "corruption", "arrested",
    ],
    "POLITIK": [
        "pilkada", "pemilu", "pilpres", "gubernur", "bupati", "walikota",
        "DPRD", "DPR", "politik", "partai", "kampanye", "debat",
        "election", "political", "governor", "parliament",
    ],
    "EKONOMI": [
        "PHK", "inflasi", "harga naik", "kemiskinan", "pengangguran",
        "investasi", "rupiah", "ekonomi", "pasar", "krisis",
        "layoff", "inflation", "poverty", "economy", "market",
    ],
    "KESEHATAN": [
        "wabah", "penyakit", "virus", "pandemi", "rumah sakit",
        "pasien", "vaksin", "DBD", "malaria", "tuberculosis",
        "outbreak", "disease", "epidemic", "hospital", "health",
    ],
}

# ── Data bencana dari BNPB (dummy seed untuk demo) ───────────────────────────
BNPB_SEED_DATA = [
    {"title":"Banjir merendam 500 rumah di Bekasi","province":"Jawa Barat","city":"Bekasi","type":"BENCANA","severity":65,"date":"2026-05-10"},
    {"title":"Gempa M5.2 guncang Palu","province":"Sulawesi Tengah","city":"Palu","type":"BENCANA","severity":72,"date":"2026-05-09"},
    {"title":"Longsor di Cianjur, 3 korban jiwa","province":"Jawa Barat","city":"Bandung","type":"BENCANA","severity":80,"date":"2026-05-08"},
    {"title":"Kebakaran hutan di Riau meluas","province":"Riau","city":"Pekanbaru","type":"BENCANA","severity":75,"date":"2026-05-07"},
    {"title":"Erupsi Gunung Merapi, status siaga","province":"DI Yogyakarta","city":"Yogyakarta","type":"BENCANA","severity":85,"date":"2026-05-06"},
    {"title":"Kekeringan melanda NTT, 10 desa terdampak","province":"Nusa Tenggara Timur","city":"Kupang","type":"BENCANA","severity":60,"date":"2026-05-05"},
    {"title":"Bentrokan antarwarga di Ternate","province":"Maluku Utara","city":"Ternate","type":"KONFLIK","severity":70,"date":"2026-05-10"},
    {"title":"Demo buruh ricuh di Surabaya","province":"Jawa Timur","city":"Surabaya","type":"KONFLIK","severity":55,"date":"2026-05-09"},
    {"title":"Penangkapan bandar narkoba besar di Medan","province":"Sumatera Utara","city":"Medan","type":"KRIMINAL","severity":68,"date":"2026-05-08"},
    {"title":"Kasus korupsi proyek jalan di Makassar","province":"Sulawesi Selatan","city":"Makassar","type":"KRIMINAL","severity":62,"date":"2026-05-07"},
]
