from flask import Flask, render_template, request, redirect, url_for, session
import os
import datetime

app = Flask(__name__)
app.secret_key = '4Dayy'  # Kunci rahasia untuk session

# Path untuk menyimpan riwayat interaksi
CHAT_HISTORY_PATH = os.path.join('data', 'chat_history.txt')

# Daftar kata-kata kotor yang ingin diblokir
BLOCKED_WORDS = ["kotor", "sakit", "jelek", "bodoh", "anjing", "bangsat", "kontol", "memek", "jancok", "asu", "bajingan", "telaso", "tolol", "monyet", "brengsek"]  # Tambahkan kata-kata lain sesuai kebutuhan

# Fungsi untuk menyimpan riwayat interaksi
def save_chat_history(user_name, user_input, bot_response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CHAT_HISTORY_PATH, 'a') as file:
        file.write(f"{timestamp} - {user_name}: {user_input}\n")
        file.write(f"{timestamp} - AI: {bot_response}\n\n")

# Fungsi untuk membaca riwayat interaksi
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_PATH):
        with open(CHAT_HISTORY_PATH, 'r') as file:
            return file.read()
    return "Riwayat interaksi kosong."

# Fungsi untuk memeriksa apakah input mengandung kata kotor
def contains_blocked_words(text):
    text = text.lower()
    for word in BLOCKED_WORDS:
        if word in text:
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
                bot_response = f"Hai, {user_name}! Nama gw Ramdan Hidayah panggil aja Dayy. Seneng banget kenalan sama lu!"
            elif user_choice == "kabar":
                bot_response = "Gue baik-baik aja, nih! Lo gimana? Hari ini seru ga?"
                session['last_question'] = "kabar"
            elif user_choice == "hobi":
                bot_response = "Gw suka banget belajar hal-hal baru dan ngobrol sama orang kaya lo. Lo sendiri, hobi lo apa?"
                session['last_question'] = "hobi"
            elif user_choice == "tentang":
                bot_response = "Gw tuh AI yang dibuat khusus buat nemenin lu. Gw di sini buat bantu lu atau sekadar ngobrol santai. Ada yang bisa gue bantu?"
            elif user_choice == "bye":
                bot_response = f"Yah, udah mau pergi aja nih? Okay deh, {user_name}! Jangan lupa balik lagi ya. Gue tunggu! "
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

# Jalankan aplikasi
if __name__ == '__main__':
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(debug=True)
