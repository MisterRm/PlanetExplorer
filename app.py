from flask import Flask, render_template, request, redirect, url_for, session
import os
import datetime

app = Flask(__name__)
app.secret_key = '4Dayy'  # Kunci rahasia untuk session

# Path untuk menyimpan riwayat interaksi dan kata kotor
CHAT_HISTORY_PATH = os.path.join('data', 'chat_history.txt')
BLOCKED_WORDS_PATH = os.path.join('data', 'blocked_words.txt')

# Fungsi untuk menyimpan riwayat interaksi
def save_chat_history(user_name, user_input, bot_response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CHAT_HISTORY_PATH, 'a') as file:
        file.write(f"{timestamp} - {user_name}: {user_input}\n")
        file.write(f"{timestamp} - AI: {bot_response}\n\n")

# Fungsi untuk membaca daftar kata kotor
def load_blocked_words():
    if os.path.exists(BLOCKED_WORDS_PATH):
        with open(BLOCKED_WORDS_PATH, 'r') as file:
            return file.read().splitlines()
    return []

# Fungsi untuk menyimpan daftar kata kotor
def save_blocked_words(words):
    with open(BLOCKED_WORDS_PATH, 'w') as file:
        for word in words:
            file.write(f"{word}\n")

# Fungsi untuk membaca riwayat chat
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_PATH):
        with open(CHAT_HISTORY_PATH, 'r') as file:
            return file.read()
    return "Riwayat interaksi kosong."

# Fungsi untuk menghapus riwayat chat
def clear_chat_history():
    with open(CHAT_HISTORY_PATH, 'w') as file:
        file.write("")

# Fungsi untuk memeriksa apakah input mengandung kata kotor
def contains_blocked_words(text):
    blocked_words = load_blocked_words()
    text = text.lower()
    for word in blocked_words:
        if word.lower() in text:
            return True
    return False

# Halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# Memulai interaksi
@app.route('/start', methods=['POST'])
def start():
    user_name = request.form['user_name']
    session['user_name'] = user_name  # Simpan nama pengguna dalam session
    session['last_question'] = None  # Reset konteks pertanyaan terakhir
    return redirect(url_for('interaction'))

# Halaman interaksi
@app.route('/interaction', methods=['GET', 'POST'])
def interaction():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        user_choice = request.form.get('user_choice')
        user_name = session.get('user_name', 'Tamu')

        # Cek kata kotor
        if user_input and contains_blocked_words(user_input):
            bot_response = "Parah lu bro! Masa sama AI ngomong kasar."
            save_chat_history(user_name, user_input, bot_response)
            chat_history = load_chat_history()
            return render_template('interaction.html', user_name=user_name, chat_history=chat_history, bot_response=bot_response)

        # Logika respons AI
        if user_input:
            last_question = session.get('last_question')
            if last_question == "kabar":
                bot_response = f"Wah, {user_input} ya? gw seneng banget denger itu!"
            elif last_question == "hobi":
                bot_response = f"Keren, {user_name}! {user_input} tuh hobi yang seru. aing juga suka belajar hal baru!"
            else:
                bot_response = "Maaf, gue ga ngerti nih. Coba pilih opsi lain, dong!"
            session['last_question'] = None
        else:
            if user_choice == "nama":
                bot_response = f"Hai, {user_name}! Nama gw Dayy. Seneng banget kenalan sama lu!"
            elif user_choice == "kabar":
                bot_response = "Gue baik-baik aja, nih! Lo gimana? Hari ini seru ga?"
                session['last_question'] = "kabar"
            elif user_choice == "hobi":
                bot_response = "Gw suka banget belajar hal-hal baru dan ngobrol sama orang kaya lo. Lo sendiri, hobi lo apa?"
                session['last_question'] = "hobi"
            elif user_choice == "tentang":
                bot_response = "Gw tuh AI yang dibuat khusus buat nemenin lu. Gw di sini buat bantu lu atau sekadar ngobrol santai. Ada yang bisa gue bantu?"
            elif user_choice == "bye":
                bot_response = f"Yah, udah mau pergi aja nih? Okay deh, {user_name}! Jangan lupa balik lagi ya. Gue tunggu!"
            else:
                bot_response = "Waduh, gue ga ngerti nih. Coba pilih opsi lain, dong!"

        # Simpan riwayat interaksi
        save_chat_history(user_name, user_input or user_choice, bot_response)

        # Muat riwayat interaksi terbaru
        chat_history = load_chat_history()

        return render_template('interaction.html', user_name=user_name, chat_history=chat_history, bot_response=bot_response)

    else:
        # Handle GET request
        user_name = session.get('user_name', 'Tamu')
        chat_history = load_chat_history()
        return render_template('interaction.html', user_name=user_name, chat_history=chat_history)

# Route untuk halaman admin
@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    blocked_words = load_blocked_words()
    chat_history = load_chat_history()
    return render_template('admin.html', blocked_words=blocked_words, chat_history=chat_history)

# Route untuk menambah kata kotor
@app.route('/add_blocked_word', methods=['POST'])
def add_blocked_word():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    new_word = request.form.get('blocked_word')
    if new_word:
        blocked_words = load_blocked_words()
        if new_word not in blocked_words:
            blocked_words.append(new_word)
            save_blocked_words(blocked_words)
    return redirect(url_for('admin'))

# Route untuk menghapus kata kotor
@app.route('/delete_blocked_word/<word>')
def delete_blocked_word(word):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    blocked_words = load_blocked_words()
    if word in blocked_words:
        blocked_words.remove(word)
        save_blocked_words(blocked_words)
    return redirect(url_for('admin'))

# Route untuk menghapus riwayat chat
@app.route('/clear_chat_history')
def clear_chat_history_route():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    clear_chat_history()
    return redirect(url_for('admin'))

# Route untuk login admin
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Autentikasi sederhana
        if username == 'kontol' and password == 'bapuk22':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Login gagal. Coba lagi."
    
    return render_template('admin_login.html')

# Route untuk logout admin
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# Jalankan aplikasi
if __name__ == '__main__':
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(debug=True)
