let CLASSROOM_DATASET = ""
let DEGREE_DATASET = ""
let RESULT_DATASET = ""
let STATS_DATASET = ""


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
                    building: CLASSROOM_DATASET[i]["Edificio"],
                    distance: result["Distance (km)"],
                    code: CLASSROOM_DATASET[i]["Code"],
                    timeslot:  result["Day"] + "-" + result["Time Slot"]
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
        STATS_DATASET =  JSON.parse(data["stats_dataset"]);
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
        let degree_name_string = "'" + degree["Denominazione CdS"].toString().replaceAll("'", " ") +"'";
        let new_row =
            '<div class="row p-2 degree-row">' +
               '<div class="col-8">' + degree_name +'</div>' +
               '<div class="col-4" style="text-align: center;"> <span id="degree-button" onclick="showContent(' + degree_code_string +', '+ degree_name_string +')">View</span> </div>' +
           '</div>';
        container.innerHTML += (new_row);
    }
}

async function shiftCoordinates(lat, lon, maxShiftMeters = 5) {

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
    let department_info = {
        lat: 0, lng: 0, name: degree_name, building: "", department_name: "",
        department_location: "", degree_level: "", number_of_students: 0
    }
    for (let degree of DEGREE_DATASET){
        if (degree["COD"] == degree_id){
            department_info.building = degree["Dipartimento"];
            let coordinates = degree["Coordinate"].toString().split(", ");
            let coordinates_shifted = await shiftCoordinates(coordinates[0], coordinates[1])
            department_info.lat = coordinates_shifted[0];
            department_info.lng = coordinates_shifted[1];
            department_info.department_name = degree["Dipartimento"];
            department_info.degree_level = degree["Livello"];
            department_info.number_of_students = degree["Participants"];
            department_info.department_location = degree["Sede Dipartimento"];
            break
        }
    }

    $("#content-title").html(`<h4 class='content-title'>Assignments for ${degree_name}</h4>`);

    await inizializzaMappa(classroom_assigned, department_info);

    $("#assignments-container").css("display", "block");
    $("#department-value").text(department_info.department_name);
    $("#department-hq-value").text(department_info.department_location);
    $("#student-number-value").text(department_info.number_of_students);
    $("#degree-level-value").text(department_info.degree_level);

    let degree_stats = {
        total_assignments: 0, in_build_assignments: 0, in_range_asssignments: 0
    }

    for (let stat of STATS_DATASET){
        if (stat["Degree Code"] == degree_id){
            degree_stats.total_assignments = parseInt(stat["Number of Assignments"]);
            degree_stats.in_build_assignments = parseInt(stat["(0, 0.5)"]);
            degree_stats.in_range_asssignments = parseInt(stat["(0, 0.5)"]) + parseInt(stat["(0.5, 1)"]);
            break
        }
    }

    let build_assigments_perc = ((degree_stats.in_build_assignments * 100) / degree_stats.total_assignments).toFixed(2);
    let range_assigments_perc = ((degree_stats.in_range_asssignments * 100) / degree_stats.total_assignments).toFixed(2);

    if (build_assigments_perc > 75){
        $("#build-assignments-value").css("background-color", "#b7e744");
    }
    if (range_assigments_perc > 75){
        $("#range-stasts-value").css("background-color", "#b7e744");
    }

    $("#total-assignments-value").text(degree_stats.total_assignments);
    $("#build-assignments-value").text(`${degree_stats.in_build_assignments} (${build_assigments_perc}%)`);
    $("#range-stasts-value").text(`${degree_stats.in_range_asssignments} (${range_assigments_perc}%)`);

    let assignments_container = document.getElementById("assignments-infobox");
    assignments_container.innerHTML = "                    " +
                "<div class=\"row header\">\n" +
                    "<div class=\"col-1\">ID</div>\n" +
                    "<div class=\"col-4\">Class Name</div>\n" +
                    "<div class=\"col-3\">Building</div>\n" +
                    "<div class=\"col-2\">Time Slot</div>\n" +
                    "<div class=\"col-2\">Distance</div>\n" +
                "</div>"
    classroom_assigned.forEach(classroom => {
        let new_row = `
                    <div class="row assignment-row">
                        <div class="col-1">${classroom["code"]}</div>
                        <div class="col-4">${classroom["name"]}</div>
                        <div class="col-3">${classroom["building"]}</div>
                        <div class="col-2">${classroom["timeslot"]}</div>
                        <div class="col-2">${classroom["distance"]}</div>
                    </div>`;

        assignments_container.innerHTML += new_row;
    });

}
