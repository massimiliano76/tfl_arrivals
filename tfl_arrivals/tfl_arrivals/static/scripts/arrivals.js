


function expectedInMinutes(ts) {
    let dateString = "2010-08-09 01:02:03"
    let regex = /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/
    let [, year, month, day, hours, minutes, seconds] = regex.exec(ts)
    let now = new Date();    
    let utc_now = (now.getTime() + now.getTimezoneOffset() * 60 * 1000);
    var expected_in_ms = new Date(year, month - 1, day, hours, minutes, seconds).getTime() - utc_now;
    return Math.ceil(expected_in_ms / (60 * 1000));
}

function createArrivalDiv(naptanId, stop_arrival_data) {
    var template = document.createElement('template');

    arrivals_list = ""
    if (stop_arrival_data.arrivals.length == 0) {
        arrivals_list = "<h3>No arrivals</h3>";
    }
    else {
        for (arr of stop_arrival_data.arrivals) {
            arrivals_list += arrivalLi = `<tr>
    <td class="arrival-data arrival-line">${arr.lineId}</td>
    <td class="arrival-data arrival-towards">${arr.towards}</td>
    <td class="arrival-data arrival-expected">${expectedInMinutes(arr.expected)}</td>
</tr>`
        }
    }

    div_text = `<div class="col col-lg-4 col-md-6 col-12 arrival-card" id="${stop_arrival_data.naptanId}_arrivals">
    <div class="card-content">
        <div class="card-content-top">        
            <div class="row align-items-center card-content-top-inner">
                <div class="col text-center arrival-station">
                    <div class="h3">
                        ${getDisplayName(stop_arrival_data.name)}
                    </div>
                    <div class="h4">
                        ${stop_arrival_data.indicator}
                    </div>
                </div>
                <div class="col h3 text-center"><a href=# onclick='removeMonitoredStationDiv("${stop_arrival_data.naptanId}")'>X</a></div>
            </div>            
        </div>
        <div class="card-content-bottom">
            <table class="arrival-table">
                <thead class="arrival-table arrival-table-head">
                    <tr>
                        <th class="arrival-header arrival-line">Line</th>
                        <th class="arrival-header arrival-towards">Towards</th>
                        <th class="arrival-header arrival-expected"></th>
                    </tr>
                </thead>
                <tbody class="arrival-table arrival-table-body">
                    ${arrivals_list}
                </tbody>
            </table>
        </div>
    </div>
</div>`

    template.innerHTML = div_text;
    return template.content.firstChild;
}

function getDisplayName(name) {
    return name.replace(" Underground Station", "");
}

function removeMonitoredStationDiv(naptan_id) {
    deleteMonitoredStopFromCookie(naptan_id);
    div = document.getElementById(naptan_id + "_arrivals");
    arrival_cards.removeChild(div);
}


function addStopArrivals(naptanId) {

    old_arrival_div = document.getElementById(naptanId + "_arrivals");

    var xhr = new XMLHttpRequest();
    xhr.open('GET', "http://localhost:5555/api/arrivals/" + naptanId, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            stop_arrival_data = JSON.parse(xhr.responseText);
            new_arrival_div = createArrivalDiv(naptanId, stop_arrival_data);

            if (old_arrival_div != null) { 
                arrival_cards.replaceChild(new_arrival_div, old_arrival_div);
            }
            else {
                arrival_cards.appendChild(new_arrival_div);
            }
        }
    }
    xhr.send();
}

window.onload = function () {
    ms = getMonitoredStopsFromCookie();
    for (stop of ms) {
        addStopArrivals(stop);
    }
};