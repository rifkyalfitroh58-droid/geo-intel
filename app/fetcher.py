"""
GEO INTEL — fetcher.py
Ambil berita dari NewsAPI, ekstrak lokasi, simpan insiden ke DB
"""
import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import NEWS_API_KEY, BNPB_SEED_DATA
from geoparser import parse_article_geo
from database import (save_incidents, update_province_stats,
                      update_hotspots, load_incidents)


def fetch_geo_data(monitor_id: int, keyword: str,
                   page_size: int = 50) -> tuple:
    """
    Ambil artikel dari NewsAPI, parse lokasi, simpan ke DB.
    Return: (n_incidents, n_locations, error_msg)
    """
    if not NEWS_API_KEY or NEWS_API_KEY == "isi_api_key_kamu_di_sini":
        return 0, 0, "NEWS_API_KEY belum diisi di config.py atau Streamlit Secrets"

    articles_raw = []
    # Coba dua query: Indonesia + keyword, dan hanya keyword
    queries = [f"{keyword} Indonesia", keyword]

    for q in queries:
        for lang in ["id", "en"]:
            try:
                resp = requests.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q":        q,
                        "pageSize": page_size,
                        "sortBy":   "publishedAt",
                        "language": lang,
                        "apiKey":   NEWS_API_KEY,
                    },
                    timeout=15,
                )
                data = resp.json()
                if data.get("status") == "ok":
                    raw = [a for a in data.get("articles",[]) if a.get("title")]
                    articles_raw.extend(raw)
            except Exception:
                continue
        if len(articles_raw) >= 20:
            break

    # Deduplikasi URL
    seen, unique = set(), []
    for art in articles_raw:
        url = art.get("url","")
        if url and url not in seen:
            seen.add(url)
            unique.append(art)

    if not unique:
        return 0, 0, "Tidak ada artikel ditemukan. Coba keyword lain."

    # Parse geo dari setiap artikel
    all_incidents = []
    for art in unique:
        incidents = parse_article_geo(art)
        all_incidents.extend(incidents)

    if not all_incidents:
        # Fallback: kalau tidak ada lokasi terdeteksi, buat satu insiden generik per artikel
        for art in unique[:20]:
            title = art.get("title","") or ""
            desc  = art.get("description","") or ""
            from geoparser import classify_incident, compute_severity
            text     = (title + " " + desc).strip()
            inc_type = classify_incident(text)
            severity = compute_severity(text, inc_type)
            all_incidents.append({
                "title":       title,
                "description": desc,
                "source":      (art.get("source") or {}).get("name","Unknown"),
                "url":         art.get("url","") or "",
                "published_at":art.get("publishedAt","") or "",
                "location":    "Indonesia",
                "province":    "Nasional",
                "lat":         -2.5,
                "lon":         118.0,
                "loc_type":    "country",
                "inc_type":    inc_type,
                "severity":    severity,
            })
        if not all_incidents:
            return 0, 0, f"{len(unique)} artikel ditemukan tapi tidak ada lokasi Indonesia terdeteksi. Coba keyword lebih spesifik."

    # Simpan ke DB
    n_saved = save_incidents(monitor_id, all_incidents)

    # Update aggregasi
    import pandas as pd
    df_inc = pd.DataFrame(all_incidents)
    df_inc["id"] = range(len(df_inc))
    update_province_stats(monitor_id, df_inc)
    update_hotspots(monitor_id, df_inc)

    n_locs = len(set(i["location"] for i in all_incidents))
    return n_saved, n_locs, None


def seed_demo_data(monitor_id: int) -> int:
    """
    Isi data demo dari BNPB seed untuk tampilan awal.
    """
    from config import CITIES, PROVINCES
    incidents = []
    for item in BNPB_SEED_DATA:
        city = item.get("city","")
        prov = item.get("province","")
        lat, lon = 0.0, 0.0
        if city in CITIES:
            lat = CITIES[city]["lat"]
            lon = CITIES[city]["lon"]
        elif prov in PROVINCES:
            lat = PROVINCES[prov]["lat"]
            lon = PROVINCES[prov]["lon"]

        incidents.append({
            "title":       item["title"],
            "description": item["title"],
            "source":      "BNPB/Demo",
            "url":         "",
            "published_at":item.get("date",""),
            "location":    city or prov,
            "province":    prov,
            "lat":         lat,
            "lon":         lon,
            "loc_type":    "city",
            "inc_type":    item["type"],
            "severity":    item["severity"],
        })

    n = save_incidents(monitor_id, incidents, is_seed=True)

    import pandas as pd
    df = pd.DataFrame(incidents)
    df["id"] = range(len(df))
    update_province_stats(monitor_id, df)
    update_hotspots(monitor_id, df)
    return n
