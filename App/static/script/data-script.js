let CLASSROOM_DATASET = ""
let DEGREE_DATASET = ""
let RESULT_DATASET = ""


async function getAssignedClassroom(degree_id){
    let result_list = [];
    for (i=0; i<RESULT_DATASET.length; i++) {
        if(RESULT_DATASET[i]["Subclass Code"].includes(degree_id)){
            result_list.push(RESULT_DATASET[i]);
        }
    }
    let classroom_data = []
    for (let result of result_list){
        for(i=0;i<CLASSROOM_DATASET.length;i++){
            if (CLASSROOM_DATASET[i]["Code"] == result["Classroom ID"]){
                let coodinates = CLASSROOM_DATASET[i]["Coordinate"].toString().split(", ")
                new_classroom = {
                    lat: coodinates[0],
                    lng : coodinates[1],
                    name: CLASSROOM_DATASET[i]["Aula"],
                    building: CLASSROOM_DATASET[i]["Edificio"]
                }
                classroom_data.push(new_classroom)
            }
        }
    }
    return classroom_data
}





async function fetchData() {
    try {
        let response = await fetch('/get_dataset');
        let data = await response.json();
        CLASSROOM_DATASET = JSON.parse(data["classroom_dataset"]);
        DEGREE_DATASET = JSON.parse(data["degree_dataset"]);
        RESULT_DATASET = JSON.parse(data["result_dataset"]);
    } catch (error) {
        console.error('Errore nel recupero dei dati:', error);
    }
    let container = document.getElementById("degree-container");
    let degree_name, degree_code
    let classroom_assigned
    for (const degree of DEGREE_DATASET){
        degree_code = degree["COD"].toString();
        degree_name = degree["Denominazione CdS"];

        let degree_code_string = "'" + degree_code +"'";
        let degree_name_string = "'" + degree["Denominazione CdS"].toString() +"'";
        let new_row =
            '<div class="row p-2 degree-row">' +
               '<div class="col-8">' + degree_name +'</div>' +
               '<div class="col-4" style="text-align: center;"> <span id="degree-button" onclick="showContent(' + degree_code_string +', '+ degree_name_string +')">View</span> </div>' +
           '</div>';
        container.innerHTML += (new_row);
    }
}

async function shiftCoordinates(lat, lon, maxShiftMeters = 5) {
    /**
     * Modifica leggermente le coordinate geografiche di un massimo di qualche metro.
     * @param {number} lat - Latitudine originale
     * @param {number} lon - Longitudine originale
     * @param {number} maxShiftMeters - Massima distanza di spostamento in metri (default: 5 metri)
     * @return {Array} Nuova coppia di coordinate [lat, lon]
     */

    // Fattore di conversione approssimativo: 1 grado di latitudine ~ 111,32 km
    const metersPerDegree = 111320;
    const shiftLat = (Math.random() * 2 - 1) * maxShiftMeters / metersPerDegree;
    const shiftLon = (Math.random() * 2 - 1) * maxShiftMeters / (metersPerDegree * Math.abs(Math.cos(lat * Math.PI / 180)));
    console.log(`Vecchie coordinate: (${lat}, ${lon})`);
    console.log(`Nuove coordinate: (${lat + shiftLat}, ${lon + shiftLon})`);

    return [parseFloat(lat) + shiftLat, parseFloat(lon) + shiftLon];
}


async function showContent(degree_id, degree_name){
    //Remove the placeholder if exists
    let placeholder = document.getElementById("result-placeholder");
    if (placeholder) {
        placeholder.style.display = "none";
    }
    let classroom_assigned = await getAssignedClassroom(degree_id);
    let department_location = {
        lat: 0, lng: 0, name: degree_name, building: ""
    }
    for (let degree of DEGREE_DATASET){
        if (degree["COD"] == degree_id){
            department_location.building = degree["Dipartimento"];
            let coordinates = degree["Coordinate"].toString().split(", ");
            let coordinates_shifted = await shiftCoordinates(coordinates[0], coordinates[1])
            department_location.lat = coordinates_shifted[0];
            department_location.lng = coordinates_shifted[1];
        }
    }

    $("#content-title").html(`<h4 class='content-title'>Assigments for ${degree_name}</h4>`);
    inizializzaMappa(classroom_assigned, department_location);
}
