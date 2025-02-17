document.addEventListener("DOMContentLoaded", function () { const searchBox = document.getElementById("searchBox"); const videoContainer = document.querySelector(".container .row"); // Tempat menampilkan video

searchBox.addEventListener("input", function () {
    let query = searchBox.value.trim();

    if (query.length === 0) {
        // Jika input kosong, tampilkan semua video
        fetchVideos();
        return;
    }

    fetch(`/search_suggestions?q=${query}`)
        .then(response => response.json())
        .then(data => {
            videoContainer.innerHTML = ""; // Hapus semua video

            if (data.length > 0) {
                data.forEach(video => {
                    let videoCard = document.createElement("div");
                    videoCard.className = "col-md-6 mb-4";
                    videoCard.innerHTML = `
                        <div class="card video-card">
                            <div class="ratio ratio-16x9">
                                <iframe class="w-100" src="${video.embed_url}" allowfullscreen></iframe>
                            </div>
                            <div class="card-body text-center">
                                <h5 class="card-title text-light">${video.title}</h5>
                            </div>
                        </div>
                    `;
                    videoContainer.appendChild(videoCard);
                });
            } else {
                videoContainer.innerHTML = "<p class='text-center mt-4'>Tidak ada video ditemukan.</p>";
            }
        });
});

function fetchVideos() {
    fetch("/")
        .then(response => response.text())
        .then(html => {
            let parser = new DOMParser();
            let doc = parser.parseFromString(html, "text/html");
            let allVideos = doc.querySelector(".container .row").innerHTML;
            videoContainer.innerHTML = allVideos;
        });
}

});

