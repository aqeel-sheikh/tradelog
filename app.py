from flask import Flask, url_for, render_template, redirect, request
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_price REAL,
                exit_price REAL,
                position_size REAL,
                emotion TEXT
            )
        ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * from trades')
    trades = cursor.fetchall()
    conn.close()
    return render_template('index.html', trades=trades)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)