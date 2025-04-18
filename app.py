from flask import Flask, render_template

app = Flask(__name__)

planets = [
    {
        "name": "Merkurius",
        "image": "merkurius.jpg",
        "desc": """
        Merkurius adalah planet terkecil di tata surya dan terdekat dengan Matahari. 
        Dengan diameter hanya 4.880 km, ia bahkan lebih kecil dari beberapa bulan planet lain.
        Planet ini menyelesaikan orbitnya mengelilingi Matahari hanya dalam 88 hari Bumi,
        tetapi satu hari di Merkurius (satu rotasi penuh) memakan waktu 59 hari Bumi.
        Suhu permukaannya ekstrem: mencapai 430°C di siang hari dan -180°C di malam hari.
        Permukaannya berbatu dan dipenuhi kawah akibat tabrakan meteor.
        """,
    },
    {
        "name": "Venus",
        "image": "venus.jpg",
        "desc": """
        Venus, si "bintang kejora", adalah planet terpanas di tata surya dengan suhu permukaan 
        mencapai 465°C—lebih panas daripada Merkurius! Atmosfernya tebal dan beracun, 
        terdiri dari 96% karbon dioksida dengan awan asam sulfat. Tekanan di permukaannya 
        92 kali lebih kuat daripada di Bumi. Venus berotasi sangat lambat: satu hari di Venus 
        lebih panjang daripada satu tahunnya! Arah rotasinya juga terbalik (dari timur ke barat).
        """,
    },
    {
        "name": "Bumi",
        "image": "bumi.jpg",
        "desc": """
        Bumi adalah planet ketiga dari Matahari dan satu-satunya yang diketahui mendukung kehidupan.
        Permukaannya 70% tertutup air, dan atmosfernya kaya nitrogen serta oksigen.
        Memiliki satelit alami besar bernama Bulan yang memengaruhi pasang surut laut.
        Bumi menyelesaikan satu orbit dalam 365,25 hari (tahun tropis) dan berotasi setiap 24 jam.
        Lapisan ozonnya melindungi kehidupan dari radiasi Matahari yang berbahaya.
        """,
    },
    {
        "name": "Mars",
        "image": "mars.jpg",
        "desc": """
        Mars, si "planet merah", dijuluki demikian karena kandungan besi oksida di permukaannya.
        Memiliki gunung tertinggi di tata surya (Olympus Mons) dan lembah terbesar (Valles Marineris).
        Atmosfernya tipis dan dingin (-60°C rata-rata), dengan musim seperti Bumi.
        Dua satelit alaminya, Phobos dan Deimos, berbentuk tidak beraturan seperti kentang.
        Mars menjadi target utama eksplorasi manusia, dengan rencana misi berawak di masa depan.
        """,
    },
    # Contoh planet lain (bisa ditambahkan):
    {
        "name": "Jupiter",
        "image": "jupiter.jpg",
        "desc": """
        Jupiter adalah planet terbesar di tata surya, dengan volume 1.300 kali Bumi.
        Terkenal dengan Bintik Merah Raksasa—badai raksasa yang telah berlangsung selama 400 tahun.
        Memiliki 95 satelit alami, termasuk Ganymede (bulan terbesar di tata surya).
        Atmosfernya terdiri dari hidrogen dan helium, dengan angin super kencang (600 km/jam).
        Jupiter membantu melindungi Bumi dengan gravitasinya yang menyerap komet dan asteroid.
        """,
    }
]

@app.route('/')
def index():
    return render_template("index.html", planets=planets)

@app.route('/planet/<name>')
def planet(name):
    planet_data = next((p for p in planets if p["name"].lower() == name.lower()), None)
    if not planet_data:
        return "Planet tidak ditemukan", 404
    return render_template("planet.html", planet=planet_data)

@app.route("/tentang")
def tentang():
    return render_template("tentang.html")

@app.route("/kontak")
def kontak():
    return render_template("kontak.html")

if __name__ == '__main__':
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(debug=True)
