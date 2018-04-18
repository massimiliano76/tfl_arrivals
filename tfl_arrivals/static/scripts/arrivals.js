


function expectedInMinutes(ts) {
    let dateString = "2010-08-09 01:02:03"
    let regex = /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/
    let [, year, month, day, hours, minutes, seconds] = regex.exec(ts)
    let now = new Date();
    let utc_now = (now.getTime() + now.getTimezoneOffset() * 60 * 1000);
    var expected_in_ms = new Date(year, month - 1, day, hours, minutes, seconds).getTime() - utc_now;
    if (expected_in_ms <= 15) {
        return "due";
    }
    else {
        return Math.ceil(expected_in_ms / (60 * 1000));
    }
}

function createArrivalDiv(naptanId) {
    var template = document.createElement('template');
    id_stem = naptanId + "_arrivals"
    div_text = `<div class="col col-lg-4 col-md-6 col-12 arrival-card" id="${id_stem}">
    <div class="card-content">
        <div class="card-content-top">
            <div class="row align-items-center card-content-top-inner">
                <div class="col text-center arrival-station">
                    <div class="h3" id="${id_stem}_name">
                    </div>
                </div>
                <div class="col col-1 h3 text-center"><a href=# onclick='removeMonitoredStationDiv("${naptanId}")'>&times;</a></div>
            </div>
        </div>
        <div class="card-content-bottom align-items-center">
            <div class="h4 align-items-center indicator invisible" id="${id_stem}_indicator">
            </div >
            <table class="arrival-table" id="${id_stem}_table">
                <tbody class="arrival-table arrival-table-body" id="${id_stem}_list">
                </tbody>
            </table>
        </div>
    </div>
</div>`

    template.innerHTML = div_text;
    return template.content.firstChild;
}

function createArrivalList(arrivals, id) {
    var template = document.createElement('template');

    arrivals_list = ""
    if (stop_arrival_data.arrivals.length == 0) {
        arrivals_list = `<div id="${id}"><h3>No arrivals</h3></div>`;
    }
    else {
        arrivals_list = `<tbody class="arrival-table arrival-table-body" id="${id}">`
        for (arr of arrivals) {
            dest = (arr.towards === "null") ? "Terminating here" : getDisplayName(arr.destination_name);
            arrivals_list += `<tr>
                <td class="arrival-data arrival-line">${arr.lineId}</td>
                <td class="arrival-data arrival-towards">${dest}</td>
                <td class="arrival-data arrival-expected">${expectedInMinutes(arr.expected)}</td>
            </tr>`
        }
        arrivals_list += '</tbody>'
    }

    template.innerHTML = arrivals_list;
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


function fillStopData(naptanId) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', api_host() + "/api/stop/" + naptanId, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.responseText == "")
                return;

            stop_data = JSON.parse(xhr.responseText);
            if (document.getElementById(naptanId + "_arrivals") != null) {
                document.getElementById(naptanId + "_arrivals_name").innerHTML = getDisplayName(stop_data["name"]);
                indicatorDiv = document.getElementById(naptanId + "_arrivals_indicator");
                indicatorText = stop_data["stop_letter"];
                if (indicatorText != "") {
                    indicatorDiv.classList.remove("invisible");
                    indicatorDiv.innerHTML = indicatorText;
                }
            }
        }
    }
    xhr.send();
}

function fillArrivals(naptanId) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', api_host() + "/api/arrivals/" + naptanId, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.responseText == "")
                return;

            stop_arrival_data = JSON.parse(xhr.responseText);
            if (stop_arrival_data != null) {
                id = naptanId + "_arrivals_list";
                old_list = document.getElementById(id);
                table = document.getElementById(naptanId + "_arrivals_table");
                new_list = createArrivalList(stop_arrival_data.arrivals, id);
                table.replaceChild(new_list, old_list);
            }
        }
    }
    xhr.send();
}

function refreshArrivalDivs(repeat = true) {
    ms = getMonitoredStopsFromCookie();
    for (stop of ms) {
        div = document.getElementById(stop + "_arrivals");
        if (div == null) {
            arrival_cards.appendChild(createArrivalDiv(stop));
        }
    }

    for (stop of ms) {
        fillStopData(stop);
    }

    for (stop of ms) {
        fillArrivals(stop);
    }

    if (repeat) {
        setTimeout(refreshArrivalDivs, 15000)
    }
};


window.onload = refreshArrivalDivs