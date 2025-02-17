document.addEventListener("DOMContentLoaded", function () {
    var chatButton = document.getElementById("chat-button");
    var chatContainer = document.createElement("div");

    chatContainer.id = "chat-container";
    chatContainer.style.position = "fixed";
    chatContainer.style.bottom = "80px";
    chatContainer.style.right = "20px";
    chatContainer.style.background = "white";
    chatContainer.style.padding = "15px";
    chatContainer.style.borderRadius = "10px";
    chatContainer.style.width = "320px";
    chatContainer.style.boxShadow = "0px 5px 15px rgba(0, 0, 0, 0.2)";
    chatContainer.style.display = "none"; 
    chatContainer.style.opacity = "0"; 
    chatContainer.style.transform = "translateY(20px)";
    chatContainer.style.transition = "opacity 0.3s ease-out, transform 0.3s ease-out";
    
    chatContainer.innerHTML = `
        <h5 style="text-align: center; font-weight: bold;">🤖 Chatbot</h5>
        <div id="chat-messages" class="chat-box"></div>
        <div id="chat-options">
            <button id="harga-premium" class="chat-btn">💰 Harga Premium</button>
            <button id="cara-bayar" class="chat-btn">💳 Cara Bayar</button>
            <button id="keuntungan-premium" class="chat-btn">✨ Keuntungan Premium</button>
            <button id="tutorial-nonton" class="chat-btn">📺 Tutorial Nonton</button>
        </div>
    `;
    document.body.appendChild(chatContainer);

    // Tambahkan CSS untuk animasi & efek modern
    var style = document.createElement("style");
    style.innerHTML = `
        /* Kotak chat */
        .chat-box {
            max-height: 250px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
            background: #f8f9fa;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        /* Balon chat dengan animasi */
        .chat-message {
            max-width: 80%;
            padding: 8px 12px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
            display: inline-block;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
            opacity: 0;
            transform: translateY(10px);
            animation: fadeInUp 0.3s forwards;
        }

        /* Pesan chatbot */
        .bot-message {
            align-self: flex-start;
            background: #007bff;
            color: white;
        }

        /* Pesan pengguna */
        .user-message {
            align-self: flex-end;
            background: #e9ecef;
            color: black;
        }

        /* Animasi pesan */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Tombol chatbot lebih modern */
        #chat-options {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 10px;
        }

        .chat-btn {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 6px;
            background: #007bff;
            color: white;
            cursor: pointer;
            font-size: 14px;
            transition: 0.3s;
            position: relative;
            overflow: hidden;
        }

        /* Efek tombol saat diklik */
        .chat-btn:active {
            transform: scale(0.95);
        }

        /* Efek muncul chatbot */
        .show-chat {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);

    // Tampilkan/Sembunyikan Chatbox dengan efek animasi
    chatButton.addEventListener("click", function () {
        if (chatContainer.style.display === "none") {
            chatContainer.style.display = "block";
            setTimeout(() => chatContainer.classList.add("show-chat"), 50);
        } else {
            chatContainer.classList.remove("show-chat");
            setTimeout(() => chatContainer.style.display = "none", 300);
        }
    });

    // Fungsi untuk menampilkan pesan dengan animasi
    function addMessage(text, isBot = true) {
        var chatMessages = document.getElementById("chat-messages");
        var message = document.createElement("div");
        message.classList.add("chat-message");
        message.classList.add(isBot ? "bot-message" : "user-message");
        message.innerHTML = text;
        chatMessages.appendChild(message);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll ke bawah
    }

    // Event listener untuk tombol chatbot
    document.getElementById("harga-premium").addEventListener("click", function () {
        addMessage("💰 Harga Premium: Rp 10.000/bulan atau Rp 100.000/tahun.");
    });

    document.getElementById("cara-bayar").addEventListener("click", function () {
        addMessage("💳 Cara Bayar: Bisa melalui GoPay, Dana. <a href='https://t.me/oembayaranWeb' target='_blank' style='color: yellow; text-decoration: underline;'>Lakukan Pembayaran Sekarang</a>");
    });

    document.getElementById("keuntungan-premium").addEventListener("click", function () {
        addMessage("✨ Keuntungan Premium: Akses tanpa iklan, kualitas video HD, dan fitur eksklusif lainnya. <a href='https://t.me/oembayaranWeb' target='_blank' style='color: yellow; text-decoration: underline;'>Lakukan Pembayaran Sekarang</a>");
    });

    document.getElementById("tutorial-nonton").addEventListener("click", function () {
        addMessage("📺 Klik di sini untuk melihat tutorial: <a href='/tutorial' target='_blank' style='color: yellow; text-decoration: underline;'>Tutorial Nonton</a>");
    });
});