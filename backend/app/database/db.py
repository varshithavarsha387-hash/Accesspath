import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "accesspath.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Barriers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS barriers (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        photo_url TEXT,
        timestamp TEXT NOT NULL,
        reporter TEXT NOT NULL,
        ai_confidence REAL NOT NULL,
        verification_status TEXT NOT NULL,
        temporary INTEGER NOT NULL,
        expires_at TEXT,
        severity TEXT NOT NULL,
        impact_summary TEXT NOT NULL
    )
    ''')
    
    # User Profile table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_profiles (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        profile_json TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    # Routes cache/history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS routes_history (
        id TEXT PRIMARY KEY,
        from_name TEXT NOT NULL,
        to_name TEXT NOT NULL,
        route_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def seed_initial_barriers_if_empty():
    from .seed_data import INITIAL_BARRIERS
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM barriers")
    count = cursor.fetchone()[0]
    
    if count == 0:
        for b in INITIAL_BARRIERS:
            cursor.execute('''
            INSERT INTO barriers (
                id, type, title, description, latitude, longitude, photo_url,
                timestamp, reporter, ai_confidence, verification_status,
                temporary, expires_at, severity, impact_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                b["id"], b["type"], b["title"], b["description"],
                b["latitude"], b["longitude"], b.get("photo_url"),
                b["timestamp"], b["reporter"], b["ai_confidence"],
                b["verification_status"], 1 if b["temporary"] else 0,
                b.get("expires_at"), b["severity"], b["impact_summary"]
            ))
        conn.commit()
    conn.close()

def get_all_barriers(include_resolved: bool = False) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if include_resolved:
        cursor.execute("SELECT * FROM barriers ORDER BY timestamp DESC")
    else:
        cursor.execute("SELECT * FROM barriers WHERE verification_status != 'Resolved' ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "type": r["type"],
            "title": r["title"],
            "description": r["description"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "photo_url": r["photo_url"],
            "timestamp": r["timestamp"],
            "reporter": r["reporter"],
            "ai_confidence": r["ai_confidence"],
            "verification_status": r["verification_status"],
            "temporary": bool(r["temporary"]),
            "expires_at": r["expires_at"],
            "severity": r["severity"],
            "impact_summary": r["impact_summary"]
        })
    return results

def insert_barrier(barrier_dict: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO barriers (
        id, type, title, description, latitude, longitude, photo_url,
        timestamp, reporter, ai_confidence, verification_status,
        temporary, expires_at, severity, impact_summary
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        barrier_dict["id"], barrier_dict["type"], barrier_dict["title"],
        barrier_dict["description"], barrier_dict["latitude"], barrier_dict["longitude"],
        barrier_dict.get("photo_url"), barrier_dict["timestamp"], barrier_dict["reporter"],
        barrier_dict["ai_confidence"], barrier_dict["verification_status"],
        1 if barrier_dict.get("temporary", True) else 0,
        barrier_dict.get("expires_at"), barrier_dict["severity"], barrier_dict["impact_summary"]
    ))
    conn.commit()
    conn.close()
    return barrier_dict

def update_barrier_status(barrier_id: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE barriers SET verification_status = ? WHERE id = ?", (status, barrier_id))
    conn.commit()
    conn.close()

def save_user_profile(user_id: str, name: str, email: str, profile_dict: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO user_profiles (id, name, email, profile_json, updated_at)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, email, json.dumps(profile_dict), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_json FROM user_profiles WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["profile_json"])
    return None
