"""
数据库管理模块
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()

    def _ensure_db_directory(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kindergarten_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    enrollment_area TEXT,
                    source_url TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lottery_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kindergarten_id INTEGER,
                    year INTEGER,
                    total_seats INTEGER,
                    applicants INTEGER,
                    win_rate REAL,
                    source_url TEXT,
                    FOREIGN KEY (kindergarten_id) REFERENCES kindergarten_data(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address_id INTEGER,
                    keyword TEXT,
                    searched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (address_id) REFERENCES addresses(id)
                )
            ''')
            
            conn.commit()

    def add_address(self, name: str, address: str, latitude: float, longitude: float) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO addresses (name, address, latitude, longitude) VALUES (?, ?, ?, ?)',
                (name, address, latitude, longitude)
            )
            conn.commit()
            return cursor.lastrowid

    def get_addresses(self) -> List[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, address, latitude, longitude, created_at FROM addresses ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'address': row[2],
                    'latitude': row[3],
                    'longitude': row[4],
                    'created_at': row[5]
                }
                for row in rows
            ]

    def update_address(self, address_id: int, name: str, address: str, latitude: float, longitude: float):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE addresses SET name=?, address=?, latitude=?, longitude=? WHERE id=?',
                (name, address, latitude, longitude, address_id)
            )
            conn.commit()

    def delete_address(self, address_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM addresses WHERE id=?', (address_id,))
            conn.commit()

    def add_kindergarten(self, name: str, type_: str, location: str, latitude: float, longitude: float,
                         enrollment_area: str = None, source_url: str = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO kindergarten_data 
                   (name, type, location, latitude, longitude, enrollment_area, source_url) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (name, type_, location, latitude, longitude, enrollment_area, source_url)
            )
            conn.commit()
            return cursor.lastrowid

    def get_kindergarten_by_name(self, name: str) -> Optional[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, name, type, location, latitude, longitude, enrollment_area FROM kindergarten_data WHERE name=?',
                (name,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'location': row[3],
                    'latitude': row[4],
                    'longitude': row[5],
                    'enrollment_area': row[6]
                }
            return None

    def get_all_kindergartens(self) -> List[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, type, location, latitude, longitude, enrollment_area FROM kindergarten_data')
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'location': row[3],
                    'latitude': row[4],
                    'longitude': row[5],
                    'enrollment_area': row[6]
                }
                for row in rows
            ]

    def add_lottery_data(self, kindergarten_id: int, year: int, total_seats: int, 
                         applicants: int, win_rate: float, source_url: str = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO lottery_data 
                   (kindergarten_id, year, total_seats, applicants, win_rate, source_url) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (kindergarten_id, year, total_seats, applicants, win_rate, source_url)
            )
            conn.commit()
            return cursor.lastrowid

    def get_lottery_data(self, kindergarten_id: int) -> List[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT year, total_seats, applicants, win_rate FROM lottery_data 
                   WHERE kindergarten_id=? ORDER BY year DESC''',
                (kindergarten_id,)
            )
            rows = cursor.fetchall()
            return [
                {
                    'year': row[0],
                    'total_seats': row[1],
                    'applicants': row[2],
                    'win_rate': row[3]
                }
                for row in rows
            ]

    def get_latest_lottery(self, kindergarten_id: int) -> Optional[Dict]:
        data = self.get_lottery_data(kindergarten_id)
        return data[0] if data else None

    def add_search_history(self, address_id: int, keyword: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO search_history (address_id, keyword) VALUES (?, ?)',
                (address_id, keyword)
            )
            conn.commit()

    def get_search_history(self, limit: int = 20) -> List[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT sh.id, a.name, a.address, sh.keyword, sh.searched_at 
                   FROM search_history sh 
                   JOIN addresses a ON sh.address_id = a.id 
                   ORDER BY sh.searched_at DESC LIMIT ?''',
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'address_name': row[1],
                    'address': row[2],
                    'keyword': row[3],
                    'searched_at': row[4]
                }
                for row in rows
            ]

    def clear_history(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM search_history')
            conn.commit()