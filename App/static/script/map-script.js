// Riferimento alla mappa (verrà inizializzato dopo il click)
let mappa = null;

// Funzione per inizializzare e mostrare la mappa
function inizializzaMappa(listaCoordinate, secondoMarker) {
    // Mostra l'indicatore di caricamento
    document.getElementById('loading').style.display = 'block';

    // Simula un piccolo ritardo per mostrare il caricamento (opzionale)
    setTimeout(() => {
        // Nascondi l'indicatore di caricamento
        document.getElementById('loading').style.display = 'none';

        // Mostra il contenitore della mappa
        document.getElementById('mappa-container').style.display = 'block';
        // Rimuove la mappa precedente se esiste
        if (mappa) {
            mappa.remove();
        }

        document.getElementById('lista-punti').innerHTML = "";
        // Inizializza la mappa (centrata sull'Italia)
        mappa = L.map('mappa').setView([41.9028, 12.4964], 5);
        // Aggiungi il layer della mappa
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(mappa);

        // Limiti per l'auto-zoom
        const bounds = L.latLngBounds();

        // Aggiungi tutti i punti alla mappa
        listaCoordinate.forEach(punto => {
            // Crea il marker
            const marker = L.marker([punto.lat, punto.lng]).addTo(mappa);

            // Aggiungi il popup con le informazioni
            const popupContent = `
                <div class="punto-info">
                    <b>${punto.name}</b><br>
                    ${punto.building || ''}<br>
                    Lat: ${punto.lat}<br>
                    Lng: ${punto.lng}
                </div>
            `;
            marker.bindPopup(popupContent);

            // Aggiungi il punto all'elenco HTML
            const listaPunti = document.getElementById('lista-punti');
            const li = document.createElement('li');
            li.innerHTML = `<b>${punto.name}</b>: ${punto.lat}, ${punto.lng} ${punto.building ? '- ' + punto.building : ''}`;
            listaPunti.appendChild(li);

            // Espandi i limiti per includere questo punto
            bounds.extend([punto.lat, punto.lng]);
        });

        // Aggiungi il secondo marker con colore diverso, se fornito
        if (secondoMarker) {
            // Icona personalizzata per il secondo marker (colore rosso)
            const redIcon = L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });

            // Crea il marker con l'icona rossa
            const marker = L.marker([secondoMarker.lat, secondoMarker.lng], {icon: redIcon}).addTo(mappa);

            // Aggiungi il popup con le informazioni
            const popupContent = `
                <div class="punto-info">
                    <b>${secondoMarker.name}</b><br>
                    ${secondoMarker.building || ''}<br>
                    Lat: ${secondoMarker.lat}<br>
                    Lng: ${secondoMarker.lng}
                </div>
            `;
            marker.bindPopup(popupContent);

            // Aggiungi il punto all'elenco HTML
            const listaPunti = document.getElementById('lista-punti');
            const li = document.createElement('li');
            li.innerHTML = `<b style="color: red;">${secondoMarker.name}</b>: ${secondoMarker.lat}, ${secondoMarker.lng} ${secondoMarker.building ? '- ' + secondoMarker.building : ''}`;
            listaPunti.appendChild(li);

            // Espandi i limiti per includere questo punto
            bounds.extend([secondoMarker.lat, secondoMarker.lng]);
        }

        // Imposta la vista della mappa per mostrare tutti i punti
        if (listaCoordinate.length > 0 || secondoMarker) {
            mappa.fitBounds(bounds, {
                padding: [50, 50] // Aggiunge un po' di spazio intorno ai punti
            });
        }

        // Invalida le dimensioni della mappa per assicurarsi che venga renderizzata correttamente
        setTimeout(() => {
            mappa.invalidateSize();
        }, 100);
    }, 500);
}