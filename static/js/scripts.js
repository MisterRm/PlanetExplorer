// Mode Gelap & Terang
document.getElementById("themeToggle").addEventListener("click", function () {
    document.body.classList.toggle("dark-mode");
    this.innerText = document.body.classList.contains("dark-mode") ? "☀️ Mode Terang" : "🌙 Mode Gelap";
});

// Statistik Pengunjung
var ctx = document.getElementById('visitorChart').getContext('2d');
var visitorChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Sen', 'Sel', 'Rab', 'Kam', 'Jum'],
        datasets: [{
            label: 'Pengunjung',
            data: [12, 19, 7, 5, 10],
            backgroundColor: 'rgba(0, 123, 255, 0.2)',
            borderColor: 'rgba(0, 123, 255, 1)',
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: { beginAtZero: true }
        }
    }
});

document.addEventListener("DOMContentLoaded", function () {
    let menuToggle = document.getElementById("menuToggle");
    let sidebar = document.getElementById("sidebar");
    let mainContent = document.getElementById("main-content");

    menuToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
        mainContent.classList.toggle("full");
    });
});

// Notifikasi Toast
function showToast(message) {
    var toast = document.getElementById("toast");
    document.getElementById("toastMessage").innerText = message;
    toast.style.display = "block";
    setTimeout(() => { toast.style.display = "none"; }, 3000);
}

window.onload = function() {
    showToast("Selamat datang di Admin Panel!");
};