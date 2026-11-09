from datetime import datetime
import sqlite3
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder='.')

DB_NAME = 'campus.db'


def init_db():
  """Инициализация базы данных SQLite и создание таблиц (Assignment 3, Part A3)"""
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT CHECK(role IN ('Admin', 'FacilityManager', 'Viewer'))
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS Buildings (
            building_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            floors INTEGER DEFAULT 1
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS SensorLogs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            building_name TEXT NOT NULL,
            temp REAL NOT NULL,
            humidity INTEGER NOT NULL,
            co2 INTEGER NOT NULL,
            energy REAL NOT NULL,
            hvac_status TEXT NOT NULL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

  cursor.execute("SELECT COUNT(*) FROM SensorLogs")
  if cursor.fetchone()[0] == 0:
    sample_data = [
        ('Block B', 27.8, 55, 1050, 180.2, 'OFF'),
        ('C1 Building', 22.1, 42, 580, 135.4, 'ON'),
        ('Main Hall', 21.5, 40, 610, 210.0, 'ON'),
    ]
    cursor.executemany(
        """
            INSERT INTO SensorLogs (building_name, temp, humidity, co2, energy, hvac_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        sample_data,
    )

  conn.commit()
  conn.close()

@app.route('/api/logs', methods=['GET'])
def get_logs():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM SensorLogs ORDER BY log_id DESC')
  rows = cursor.fetchall()
  conn.close()

  logs_list = [dict(row) for row in rows]
  return jsonify(logs_list)

@app.route('/api/logs', methods=['POST'])
def add_log():
  data = request.json
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  cursor.execute(
      """
        INSERT INTO SensorLogs (building_name, temp, humidity, co2, energy, hvac_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
      (
          data.get('building'),
          data.get('temp'),
          data.get('humidity'),
          data.get('co2'),
          data.get('energy'),
          data.get('hvac'),
      ),
  )

  conn.commit()
  conn.close()
  return jsonify(
      {'status': 'success', 'message': 'Successfully inserted into SQLite!'}
  )


@app.route('/')
def home():
  return render_template('index.html')


if __name__ == '__main__':
  init_db()
  print('Сервер запущен! Открой в браузере: http://127.0.0.1:5000')
  app.run(debug=True)
