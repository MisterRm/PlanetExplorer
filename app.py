from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit
from flask import jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurasi Database
DATABASE = 'database.db'

# Inisialisasi SocketIO
socketio = SocketIO(app)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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

# Route Index tanpa Pagination
@app.route('/')
def index():
    query = request.args.get('q', '').strip()  # Ambil query pencarian

    with get_db() as db:
        if query:
            videos = db.execute(
                "SELECT * FROM videos WHERE title LIKE ? ORDER BY id DESC", 
                (f"%{query}%",)
            ).fetchall()
        else:
            videos = db.execute(
                "SELECT * FROM videos ORDER BY id DESC"
            ).fetchall()

    return render_template(
        'index.html',
        videos=videos,
        query=query  # Kirim query ke template
    )
    
@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])  # Jika kosong, kirim array kosong

    with get_db() as db:
        videos = db.execute(
            "SELECT * FROM videos WHERE title LIKE ? ORDER BY id DESC LIMIT 10",
            (f"%{query}%",)
        ).fetchall()

    return jsonify([{"id": v["id"], "title": v["title"], "embed_url": v["embed_url"]} for v in videos])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role']
            flash("Selamat datang, " + user['username'], "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Username atau password salah", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/kontol')
def admin_dashboard():
    if 'logged_in' not in session or session.get('role') != 'admin':
        flash("Akses ditolak", "danger")
        return redirect(url_for('login'))
    
    with get_db() as db:
        videos = db.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    
    return render_template('kontol.html', videos=videos)

@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    if 'logged_in' not in session or session.get('role') != 'admin':
        flash("Akses ditolak", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        embed_url = request.form['embed_url']

        with get_db() as db:
            db.execute("INSERT INTO videos (title, embed_url) VALUES (?, ?)", (title, embed_url))
            db.commit()

        # Emit notifikasi ke semua client yang terhubung
        socketio.emit('new_video', {'title': title, 'embed_url': embed_url})

        return redirect(url_for('admin_dashboard'))

    return render_template('add_video.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()  # Ambil input pencarian

    with get_db() as db:
        videos = db.execute(
            "SELECT * FROM videos WHERE title LIKE ? ORDER BY id DESC",
            (f"%{query}%",)
        ).fetchall()

    return render_template(
        'index.html',
        videos=videos,
        query=query
    )

@app.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    if 'logged_in' not in session or session.get('role') != 'admin':
        flash("Akses ditolak", "danger")
        return redirect(url_for('login'))

    with get_db() as db:
        db.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        db.commit()

    return redirect(url_for('admin_dashboard'))

# Route untuk menangani notifikasi real-time
@socketio.on('connect')
def handle_connect():
    print("A client has connected.")

@socketio.on('disconnect')
def handle_disconnect():
    print("A client has disconnected.")

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    port = int(os.environ.get("PORT", 8080))  # Gunakan port 8080
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
