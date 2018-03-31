
function clearHighlightedLine(list) {
    for (line of list.getElementsByTagName("li")) {
        line.classList.remove("active");
    };
}

function setHighlightedLine(list, naptan_id) {
    clearHighlightedLine(list);
    for (line of list.getElementsByTagName("li")) {
        if (line.getAttribute("data-naptan-id") == naptan_id)
            line.classList.add("active");
    };
    updateAddButtonEnabledState();
}


function showAddResultMessage(text, success) {
    row = document.createElement("div");
    row.classList = "row position-absolute justify-content-center slide-in-out";

    alert = document.createElement("div");
    alert.classList = "col-6 align-middle alert"
    alert.classList.add(success ? "alert-success" : "alert-danger");
    
    alert.innerHTML = text;
    row.appendChild(alert);

    document.body.insertBefore(row, document.body.firstChild);
    setTimeout("alert.remove();", 4000);
}

function addStop() {
    let id = selectedStop().getAttribute("data-naptan-id")
    addMonitoredStop(id);
    refreshArrivalDivs();
}

function clearStops() {
    while (stop_list.firstChild) {
        stop_list.removeChild(stop_list.firstChild);
    } 
    clearHighlightedLine(stop_list);
    updateAddButtonEnabledState();
}

function selectStop(naptan_id) {    
    setHighlightedLine(stop_list, naptan_id);
    updateAddButtonEnabledState();
}

function selectedStop() {
    for (stop of stop_list.getElementsByTagName("li")) {
        if (stop.classList.contains("active")) {
            return stop;
        }
    }

    return null;
}

function updateAddButtonEnabledState() {
    add_stop.disabled = (selectedStop() == null);
}



function loadStops(line_id) {    
    var xhr = new XMLHttpRequest();
    xhr.open('GET', api_host() + "/api/stops/" + line_id, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            stops = JSON.parse(xhr.responseText);
            clearStops();

            for (let stop of stops) {
                var li = document.createElement("li");
                var name = stop.name;
                if (stop.indicator != "") {
                    name += " (" + stop.indicator + ")";
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



function selectLine(line) {    
    loadStops(line.getAttribute("data-naptan-id"));
    setHighlightedLine(line_list, line.getAttribute("data-naptan-id"));
}


function filterItems(pattern, list) {
    var items = list.getElementsByTagName("li");

    var count = 0;
    for (i = 0; i < items.length; i++) {
        if (items[i].innerHTML.toUpperCase().indexOf(pattern.toUpperCase()) > -1) {
            items[i].style.display = "block";
            count++;
        } else {
            items[i].style.display = "none";
        }
    }
    return count;
}


function selectFirstVisible(line_list) {
    var items = line_list.getElementsByTagName("li");

    var count = 0;
    for (i = 0; i < items.length; i++) {
        if (items[i].style.display == "block") {
            selectLine(items[i]);
            return;
        }
    }
}


line_search.addEventListener('keyup', function () {
    if (filterItems(this.value, line_list) == 0) {
        clearStops();
    }
    selectFirstVisible(line_list);
});

stop_search.addEventListener('keyup', function () {
    filterItems(this.value, stop_list);
});

