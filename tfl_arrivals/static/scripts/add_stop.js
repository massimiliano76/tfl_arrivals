function clearHighlightedLine(list) {
    let li_list = list.getElementsByTagName("li");
    for (var i = 0; i < li_list.length; i++) {
        li_list[i].classList.remove("active");
    };
}

function setHighlightedLine(list, naptan_id) {
    clearHighlightedLine(list);
    let li_list = list.getElementsByTagName("li");
    for (var i = 0; i < li_list.length; i++) {
        if (li_list[i].getAttribute("data-naptan-id") == naptan_id)
            li_list[i].classList.add("active");
    };
}

function addStop() {
    let id = selectedStop().getAttribute("data-naptan-id")
    addMonitoredStop(id);
    window.scrollTo(0, document.body.scrollHeight);
    refreshArrivalDivs(false);
}

function clearStops() {
    while (stop_list.firstChild) {
        stop_list.removeChild(stop_list.firstChild);
    }
    clearHighlightedLine(stop_list);
}

function selectStop(naptan_id) {
    setHighlightedLine(stop_list, naptan_id);
    addStop();
    $(stop_add_screen).modal('hide');
}

function selectedStop() {
  let li_list = stop_list.getElementsByTagName("li");
  for (var i = 0; i < li_list.length; i++) {
    if (li_list[i].classList.contains("active")) {
      return li_list[i];
    }
  }
  return null;
}

const line_names = {
  "bakerloo": "Bakerloo",
  "central": "Central",
  "circle": "Circle",
  "district": "District",
  "elizabeth": "Elizabeth",
  "hammersmith-city": "Hammersmith & City",
  "jubilee": "Jubilee",
  "metropolitan": "Metropolitan",
  "northern": "Northern",
  "piccadilly": "Piccadilly",
  "victoria": "Victoria",
  "waterloo-city": "Waterloo & city"
}

function createBadges(stop) {
  let tubes = stop.lines_tube == "" ? "" : stop.lines_tube.split(",").
    map(x => `<span class="badge badge-secondary badge-tube-${x}">${line_names[x]}</span>`).
    join(" ");

  let buses = stop.lines_bus == "" ? "" : stop.lines_bus.split(",").
    map(x => `<span class="badge badge-secondary badge-bus">${x.toUpperCase()}</span>`).
    join(" ");

  let dlr = stop.mode_dlr ? `<span class="badge badge-secondary badge-dlr">DLR</span>` : "";
  let overground = stop.mode_overground ? `<span class="badge badge-secondary badge-overground">Overground</span>` : "";
  let tram = stop.mode_tram ? `<span class="badge badge-secondary badge-tram">Tram</span>` : "";

  let all = (tubes + " " + overground + " " + dlr + " " + tram).trim();
  if(all == "") {
    all = buses;
  }

  return all == "" ? "" : "<br>" + all;
}


function loadStops(query) {
    let xhr = new XMLHttpRequest();

    xhr.open('GET', api_host() + "/api/stop_search/" + query, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            stops = JSON.parse(xhr.responseText);
            clearStops();
            if(stops.length > 0) {
              add_stop_help.style.display = "none";
              stop_list.style.display = "flex";
            }

            for (let stop of stops) {

                var name = stop.name.replace(" Underground Station", "");
                if (stop.stop_letter != "" && stop.stop_letter.length <= 2) {
                    name += " (" + stop.stop_letter + ")";
                }
                let li = document.createElement("li");
                let badges = createBadges(stop);
                if(badges == "")
                  continue;
                li.innerHTML = name + badges;
                li.classList.add("list-group-item");
                li.setAttribute("data-naptan-id", stop.naptan_id);
                li.onclick = function () { selectStop(stop.naptan_id); }
                stop_list.appendChild(li);
            }
        }
    }
    xhr.send();
}

var delayedSearch = null;
stop_search.addEventListener('keyup', function (event) {
    clearTimeout(delayedSearch);
    if(event.key === "Enter") {
        loadStops(stop_search.value);
    }
    else if(stop_search.value.length >= 3) {
        delayedSearch = setTimeout( () => loadStops(stop_search.value), 700);
    }
});

search_icon.addEventListener('click', function () {
    console.log("stop_icon click");
    clearTimeout(delayedSearch);
    loadStops(stop_search.value);
});
