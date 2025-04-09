let mappa = null;


function inizializzaMappa(listaCoordinate, secondoMarker) {
    document.getElementById('loading').style.display = 'block';

    setTimeout(() => {
        document.getElementById('loading').style.display = 'none';

        document.getElementById('mappa-container').style.display = 'block';
        if (mappa) {
            mappa.remove();
        }
        mappa = L.map('mappa').setView([41.9028, 12.4964], 5);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(mappa);

        const bounds = L.latLngBounds();

        listaCoordinate.forEach(punto => {
            const marker = L.marker([punto.lat, punto.lng]).addTo(mappa);

            const popupContent = `
                <div class="punto-info">
                    <b>${punto.name}</b><br>
                    ${punto.building || ''}<br>
                    Lat: ${punto.lat}<br>
                    Lng: ${punto.lng}
                </div>
            `;
            marker.bindPopup(popupContent);

            bounds.extend([punto.lat, punto.lng]);
        });

        if (secondoMarker) {
            const redIcon = L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });

            const marker = L.marker([secondoMarker.lat, secondoMarker.lng], {icon: redIcon}).addTo(mappa);

            const popupContent = `
                <div class="punto-info">
                    <b>${secondoMarker.name}</b><br>
                    ${secondoMarker.building || ''}<br>
                    Lat: ${secondoMarker.lat}<br>
                    Lng: ${secondoMarker.lng}
                </div>
            `;
            marker.bindPopup(popupContent);
            bounds.extend([secondoMarker.lat, secondoMarker.lng]);
        }

        if (listaCoordinate.length > 0 || secondoMarker) {
            mappa.fitBounds(bounds, {
                padding: [50, 50]
            });
        }

        setTimeout(() => {
            mappa.invalidateSize();
        }, 100);
    }, 100);
}