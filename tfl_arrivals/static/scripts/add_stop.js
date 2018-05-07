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

                var li = document.createElement("li");
                var name = stop.name.replace(" Underground Station", "");
                if (stop.stop_letter != "" && stop.stop_letter.length <= 2) {
                    name += " (" + stop.stop_letter + ")";
                }
                li.appendChild(document.createTextNode(name));
                li.classList.add("list-group-item");
                li.setAttribute("data-naptan-id", stop.naptan_id);
                li.onclick = function () { selectStop(stop.naptan_id); }
                stop_list.appendChild(li);
            }
        }
    }
    xhr.send();
}

stop_search.addEventListener('keyup', function () {
    if(stop_search.value.length >= 3) {
      loadStops(stop_search.value);
    }
});
