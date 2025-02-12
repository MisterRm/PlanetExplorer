document.addEventListener("DOMContentLoaded", function () {
    const chatButton = document.getElementById("chat-button");
    const chatContainer = document.getElementById("chat-container");
    const chatMessages = document.getElementById("chat-messages");

    function sendMessage(message) {
        // Tampilkan loading sebelum mendapatkan respons
        chatMessages.innerHTML += `<p><strong>Anda:</strong> ${message}</p>`;
        chatMessages.innerHTML += `<p><em>Bot sedang mengetik...</em></p>`;

        fetch(`/chatbot?message=${encodeURIComponent(message)}`)
            .then(response => response.json())
            .then(data => {
                chatMessages.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                chatMessages.innerHTML += `<p><strong>Bot:</strong> ❌ Terjadi kesalahan, coba lagi.</p>`;
            });
    }

    chatButton.addEventListener("click", function () {
        chatContainer.classList.toggle("d-none");
    });

    document.getElementById("harga-premium").addEventListener("click", function () {
        sendMessage("harga premium");
    });

    document.getElementById("cara-bayar").addEventListener("click", function () {
        sendMessage("cara bayar");
    });

    document.getElementById("keuntungan-premium").addEventListener("click", function () {
        sendMessage("keuntungan premium");
    });
});