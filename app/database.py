"""
GEO INTEL — database.py
Operasi database SQLite untuk penyimpanan insiden geospasial
"""
import sqlite3
import os, sys
import pandas as pd
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def ensure_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS monitors (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword    TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active  INTEGER DEFAULT 1,
            total_hits INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS incidents (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id   INTEGER,
            title        TEXT,
            description  TEXT,
            source       TEXT,
            url          TEXT,
            published_at TEXT,
            location     TEXT,
            province     TEXT,
            lat          REAL,
            lon          REAL,
            loc_type     TEXT DEFAULT 'city',
            inc_type     TEXT DEFAULT 'LAINNYA',
            severity     REAL DEFAULT 0.0,
            is_seed      INTEGER DEFAULT 0,
            FOREIGN KEY(monitor_id) REFERENCES monitors(id)
        );

        CREATE TABLE IF NOT EXISTS province_stats (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id   INTEGER,
            province     TEXT,
            incident_count INTEGER DEFAULT 0,
            avg_severity REAL DEFAULT 0.0,
            dominant_type TEXT,
            updated_at   TEXT,
            FOREIGN KEY(monitor_id) REFERENCES monitors(id)
        );

        CREATE TABLE IF NOT EXISTS hotspots (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            monitor_id INTEGER,
            location   TEXT,
            province   TEXT,
            lat        REAL,
            lon        REAL,
            count      INTEGER DEFAULT 0,
            avg_sev    REAL DEFAULT 0.0,
            inc_type   TEXT,
            FOREIGN KEY(monitor_id) REFERENCES monitors(id)
        );
    """)
    conn.commit()
    conn.close()


# ── Monitor CRUD ──────────────────────────────────────────────────────────────
def add_monitor(keyword: str) -> int:
    conn = get_conn()
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cur  = conn.execute(
        "INSERT INTO monitors (keyword, created_at) VALUES (?,?)", (keyword.strip(), now)
    )
    mid = cur.lastrowid
    conn.commit()
    conn.close()
    return mid

def get_monitors() -> pd.DataFrame:
    try:
        conn = get_conn()
        df   = pd.read_sql("SELECT * FROM monitors WHERE is_active=1 ORDER BY created_at DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

def delete_monitor(mid: int):
    conn = get_conn()
    for tbl in ["hotspots","province_stats","incidents"]:
        conn.execute(f"DELETE FROM {tbl} WHERE monitor_id=?", (mid,))
    conn.execute("DELETE FROM monitors WHERE id=?", (mid,))
    conn.commit()
    conn.close()


# ── Incident CRUD ─────────────────────────────────────────────────────────────
def save_incidents(monitor_id: int, incidents: list, is_seed: bool = False) -> int:
    conn = get_conn()
    cur  = conn.cursor()
    n    = 0
    for inc in incidents:
        try:
            cur.execute("""
                INSERT INTO incidents
                (monitor_id,title,description,source,url,published_at,
                 location,province,lat,lon,loc_type,inc_type,severity,is_seed)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                monitor_id,
                inc.get("title",""),
                inc.get("description",""),
                inc.get("source",""),
                inc.get("url",""),
                inc.get("published_at",""),
                inc.get("location",""),
                inc.get("province",""),
                inc.get("lat", 0.0),
                inc.get("lon", 0.0),
                inc.get("loc_type","city"),
                inc.get("inc_type","LAINNYA"),
                inc.get("severity", 0.0),
                1 if is_seed else 0,
            ))
            n += 1
        except Exception:
            continue
    # Update total_hits monitor
    conn.execute("UPDATE monitors SET total_hits=total_hits+? WHERE id=?", (n, monitor_id))
    conn.commit()
    conn.close()
    return n

def load_incidents(monitor_id: int) -> pd.DataFrame:
    try:
        conn = get_conn()
        df   = pd.read_sql(
            "SELECT * FROM incidents WHERE monitor_id=? ORDER BY published_at DESC",
            conn, params=(monitor_id,)
        )
        conn.close()
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()

def load_all_incidents() -> pd.DataFrame:
    try:
        conn = get_conn()
        df   = pd.read_sql("""
            SELECT i.*, m.keyword as monitor_keyword
            FROM incidents i
            JOIN monitors m ON i.monitor_id = m.id
            ORDER BY i.published_at DESC
        """, conn)
        conn.close()
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()


# ── Province stats ────────────────────────────────────────────────────────────
def update_province_stats(monitor_id: int, df_inc: pd.DataFrame):
    if df_inc.empty:
        return
    conn = get_conn()
    conn.execute("DELETE FROM province_stats WHERE monitor_id=?", (monitor_id,))
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    stats = df_inc.groupby("province").agg(
        incident_count=("id","count"),
        avg_severity=("severity","mean"),
    ).reset_index()

    for _, row in stats.iterrows():
        dom = df_inc[df_inc["province"]==row["province"]]["inc_type"].mode()
        dom_type = dom.iloc[0] if not dom.empty else "LAINNYA"
        conn.execute("""
            INSERT INTO province_stats
            (monitor_id,province,incident_count,avg_severity,dominant_type,updated_at)
            VALUES (?,?,?,?,?,?)
        """, (monitor_id, row["province"],
              int(row["incident_count"]),
              round(float(row["avg_severity"]),1),
              dom_type, now))
    conn.commit()
    conn.close()

def load_province_stats(monitor_id: int) -> pd.DataFrame:
    try:
        conn = get_conn()
        df   = pd.read_sql(
            "SELECT * FROM province_stats WHERE monitor_id=? ORDER BY incident_count DESC",
            conn, params=(monitor_id,)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# ── Hotspots ──────────────────────────────────────────────────────────────────
def update_hotspots(monitor_id: int, df_inc: pd.DataFrame):
    if df_inc.empty:
        return
    conn = get_conn()
    conn.execute("DELETE FROM hotspots WHERE monitor_id=?", (monitor_id,))

    hs = df_inc.groupby(["location","province","lat","lon"]).agg(
        count=("id","count"),
        avg_sev=("severity","mean"),
    ).reset_index()

    for _, row in hs.iterrows():
        dom = df_inc[df_inc["location"]==row["location"]]["inc_type"].mode()
        dom_type = dom.iloc[0] if not dom.empty else "LAINNYA"
        conn.execute("""
            INSERT INTO hotspots
            (monitor_id,location,province,lat,lon,count,avg_sev,inc_type)
            VALUES (?,?,?,?,?,?,?,?)
        """, (monitor_id, row["location"], row["province"],
              float(row["lat"]), float(row["lon"]),
              int(row["count"]), round(float(row["avg_sev"]),1), dom_type))
    conn.commit()
    conn.close()

def load_hotspots(monitor_id: int) -> pd.DataFrame:
    try:
        conn = get_conn()
        df   = pd.read_sql(
            "SELECT * FROM hotspots WHERE monitor_id=? ORDER BY count DESC",
            conn, params=(monitor_id,)
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# ── Global stats ──────────────────────────────────────────────────────────────
def get_global_stats() -> dict:
    try:
        conn  = get_conn()
        total = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
        high  = conn.execute("SELECT COUNT(*) FROM incidents WHERE severity>=75").fetchone()[0]
        provs = conn.execute("SELECT COUNT(DISTINCT province) FROM incidents").fetchone()[0]
        avg_s = conn.execute("SELECT AVG(severity) FROM incidents").fetchone()[0] or 0.0
        top_t = conn.execute("""
            SELECT inc_type, COUNT(*) as c FROM incidents
            GROUP BY inc_type ORDER BY c DESC LIMIT 1
        """).fetchone()
        conn.close()
        return {
            "total":       total,
            "high_sev":    high,
            "provinces":   provs,
            "avg_severity":round(avg_s, 1),
            "top_type":    top_t[0] if top_t else "N/A",
        }
    except Exception:
        return {"total":0,"high_sev":0,"provinces":0,"avg_severity":0.0,"top_type":"N/A"}
