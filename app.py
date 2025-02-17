from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import os
import time
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurasi Database
DATABASE = 'database.db'

# Inisialisasi SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Simpan daftar pengunjung aktif { session_id: timestamp }
active_users = {}

# Timeout user dalam 30 detik jika tidak ada aktivitas
USER_TIMEOUT = 30

def get_db():
    """Membuka koneksi ke database SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inisialisasi database jika belum ada."""
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            embed_url TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS visitor_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            count INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            action TEXT NOT NULL
        );
        """)
        db.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
        db.commit()

# Data chatbot dalam JSON
chatbot_responses = {
    "harga premium": "💰 Paket premium mulai dari Rp10.000 per bulan. Bayar di sini: <a href='https://example.com/bayar'>Klik untuk membayar</a>",
    "cara bayar": "💳 Pembayaran bisa lewat Dana, OVO, dan bank transfer. Cek petunjuk lengkap di sini: <a href='https://example.com/pembayaran'>Panduan Pembayaran</a>",
    "keuntungan premium": "✨ Keuntungan premium: Bebas iklan, kualitas HD, dan akses eksklusif!",
    "Langganan": "hallo",
    "default": "❌ Maaf, saya tidak mengerti. <a href='https://wa.me/6281234567890'>Klik di sini untuk chat dengan admin</a>"
}

@app.route('/chatbot')
def chatbot():
    message = request.args.get('message', '').lower()
    response = chatbot_responses.get(message, chatbot_responses["default"])
    return jsonify({"response": response})

@app.route('/')
def index():
    """Halaman utama dengan daftar video dan pencarian real-time"""
    query = request.args.get('q', '').strip()

    with get_db() as db:
        if query:
            videos = db.execute(
                "SELECT * FROM videos WHERE title LIKE ? ORDER BY id DESC",
                (f"%{query}%",)
            ).fetchall()
        else:
            videos = db.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()

    return render_template('index.html', videos=videos, query=query)

@app.route('/search_suggestions')
def search_suggestions():
    """Mengembalikan hasil pencarian real-time"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    with get_db() as db:
        videos = db.execute(
            "SELECT * FROM videos WHERE title LIKE ? ORDER BY id DESC LIMIT 10",
            (f"%{query}%",)
        ).fetchall()

    return jsonify([{"id": v["id"], "title": v["title"], "embed_url": v["embed_url"]} for v in videos])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Username: {username}, Password: {password}")  # Debugging

        with get_db() as db:
            try:
                user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
                print(f"User: {user}")  # Debugging
            except sqlite3.OperationalError as e:
                print(f"Database error: {e}")  # Debugging
                flash("Terjadi kesalahan pada database. Silakan coba lagi.", "danger")
                return redirect(url_for('login'))

        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            print("Login berhasil!")  # Debugging
            flash("Selamat datang, " + user['username'], "success")
            return redirect(url_for('admin_dashboard'))
        else:
            print("Login gagal!")  # Debugging
            flash("Username atau password salah", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout admin"""
    if 'username' in session:
        with get_db() as db:
            db.execute("INSERT INTO admin_logs (timestamp, username, action) VALUES (?, ?, ?)",
                       (datetime.datetime.now(), session['username'], "Logout"))
            db.commit()

    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    """Halaman admin"""
    if 'logged_in' not in session or session.get('role') != 'admin':
        flash("Akses ditolak", "danger")
        return redirect(url_for('login'))

    with get_db() as db:
        videos = db.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()

    return render_template('admin.html', videos=videos)

@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    """Menambahkan video baru (admin)"""
    if 'logged_in' not in session or session.get('role') != 'admin':
        flash("Akses ditolak", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        embed_url = request.form['embed_url']

        with get_db() as db:
            db.execute("INSERT INTO videos (title, embed_url) VALUES (?, ?)", (title, embed_url))
            db.commit()

        socketio.emit('new_video', {'title': title, 'embed_url': embed_url})
        return redirect(url_for('admin_dashboard'))

    return render_template('add_video.html')

@app.route('/edit_video/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    """Mengedit video (admin)"""
    if 'logged_in' not in session or session.get('role') != 'admin':
        flash("Akses ditolak", "danger")
        return redirect(url_for('login'))

    with get_db() as db:
        video = db.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        embed_url = request.form['embed_url']
        with get_db() as db:
            db.execute("UPDATE videos SET title = ?, embed_url = ? WHERE id = ?", (title, embed_url, video_id))
            db.commit()
        flash("Video berhasil diperbarui!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_video.html', video=video)

@app.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    """Menghapus video dari database"""
    if 'logged_in' not in session or session.get('role') != 'admin':
        flash("Akses ditolak", "danger")
        return redirect(url_for('login'))

    with get_db() as db:
        db.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        db.commit()

    flash("Video berhasil dihapus!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/get_visitor_count')
def get_visitor_count():
    """Mengembalikan jumlah pengunjung aktif"""
    return jsonify({'visitor_count': len(active_users)})

@app.route('/admin_stats')
def admin_stats():
    """Mengambil statistik pengunjung untuk ditampilkan di grafik"""
    with get_db() as db:
        stats = db.execute("SELECT date, count FROM visitor_stats ORDER BY date DESC LIMIT 7").fetchall()
    return jsonify({'data': [{'date': s['date'], 'count': s['count']} for s in stats]})

@app.route('/admin_logs')
def admin_logs():
    """Mengambil log aktivitas admin"""
    with get_db() as db:
        logs = db.execute("SELECT * FROM admin_logs ORDER BY timestamp DESC LIMIT 10").fetchall()
    return jsonify({'logs': [{'timestamp': l['timestamp'], 'username': l['username'], 'action': l['action']} for l in logs]})

def update_visitor_stats():
    """Menyimpan jumlah pengunjung harian ke database"""
    today = datetime.date.today().strftime('%Y-%m-%d')

    with get_db() as db:
        db.execute("INSERT INTO visitor_stats (date, count) VALUES (?, 1) ON CONFLICT(date) DO UPDATE SET count = count + 1", (today,))
        db.commit()

@socketio.on('connect')
def handle_connect():
    """Menangani koneksi pengguna baru"""
    session_id = request.sid  
    active_users[session_id] = time.time()
    update_visitor_stats()
    update_active_users()

@socketio.on('disconnect')
def handle_disconnect():
    """Menangani pemutusan koneksi pengguna"""
    session_id = request.sid
    if session_id in active_users:
        del active_users[session_id]
    update_active_users()

def update_active_users():
    """Mengirim jumlah pengunjung aktif ke semua klien"""
    socketio.emit('update_visitor_count', {'visitor_count': len(active_users)})

def remove_inactive_users():
    """Menghapus pengguna yang tidak aktif setelah timeout"""
    while True:
        current_time = time.time()
        inactive_users = [sid for sid, last_active in active_users.items() if current_time - last_active > USER_TIMEOUT]

        for sid in inactive_users:
            del active_users[sid]

        update_active_users()
        socketio.sleep(USER_TIMEOUT)

socketio.start_background_task(remove_inactive_users)

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    port = int(os.environ.get("PORT", 8080))  # Gunakan port 8080
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
