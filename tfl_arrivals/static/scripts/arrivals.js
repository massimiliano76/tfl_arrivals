
var card_template;

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
    let template = document.createElement('template');
    let id_stem = naptanId + "_arrivals";
    let div_text = card_template.replace(/{{ id_stem }}/g, id_stem).
      replace(/{{ naptan_id }}/g, naptanId);
    template.innerHTML = div_text;
    return template.content.firstChild;
}

function shortLineName(s) {
  if(s == "Hammersmith & City")
    return "Ham&City";
  return s;
}

function createArrivalList(arrivals, id) {
    var template = document.createElement('template');

    arrivals_list = `<tbody class="arrival-table arrival-table-body" id="${id}">`
    if (stop_arrival_data.arrivals.length == 0) {
        arrivals_list += `<tr><td class="no-arrivals">No arrivals</td></tr>`;
    }
    else {
        for (arr of arrivals) {
            dest = (arr.towards === "null") ? "Terminating here" : getDisplayName(arr.destination_name);
            arrivals_list += `<tr>
                <td class="arrival-data arrival-line">${shortLineName(arr.lineName)}</td>
                <td class="arrival-data arrival-towards">${dest}</td>
                <td class="arrival-data arrival-expected">${expectedInMinutes(arr.expected)}</td>
            </tr>`
        }
    }
    arrivals_list += '</tbody>'

    template.innerHTML = arrivals_list;
    return template.content.firstChild;
}

const shorterNames = {
  "Hammersmith (Dist&Picc Line)": "Hammersmith (Dist&Picc)",
  "Edgware Road (Circle Line)": "Edgware Road (Circle)",
  "Hammersmith (H&C Line)": "Hammersmith (H&C)",
  "Cutty Sark (for Maritime Greenwich)": "Cutty Sark (for Maritime Gr.)",
  "Heathrow Terminals 1-2-3": "Heathrow 1-2-3",
}

function getDisplayName(name) {
    let s = name.replace(" Underground Station", "");
    s = s.replace(" DLR Station", "");
    if(s in shorterNames) {
      s = shorterNames[s];
    }
    return s;
}

function removeMonitoredStationDiv(naptan_id) {
    deleteMonitoredStop(naptan_id);
    div = document.getElementById(naptan_id + "_arrivals");
    div.classList.remove("add-card");
    div.classList.add("remove-card");
    setTimeout( () => {arrival_cards.removeChild(div)} , 500);
}

function displayStopData(naptan_id, stop_data) {
  if (document.getElementById(naptan_id + "_arrivals") != null) {
      document.getElementById(naptan_id + "_arrivals_name").innerHTML = getDisplayName(stop_data["name"]);
      stop_letter_div = document.getElementById(naptan_id + "_arrivals_stop_letter");
      stop_letter = stop_data["stop_letter"];
      if (stop_letter != "" && stop_letter.length <= 2) {
          stop_letter_div.parentElement.classList.remove("invisible");
          stop_letter_div.textContent = stop_letter;
      }
      else {
        // Add "F" for fuck
        // If the div doesn't contain anything then the layout in Firefox
        // fill be fucked up, even tough the position is relative
        // and in this branch the div is invisible...
        stop_letter_div.textContent = "F";
      }
  }
}


function fillStopData(naptan_id) {
    stored_data = localStorage.getItem(naptan_id);
    if(stored_data != null) {
      displayStopData(naptan_id, JSON.parse(stored_data));
      return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open('GET', api_host() + "/api/stop/" + naptan_id, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.responseText == "")
                return;

            stop_data = JSON.parse(xhr.responseText);
            localStorage.setItem(naptan_id, xhr.responseText);
            displayStopData(naptan_id, stop_data);
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
                loader = document.getElementById(naptanId + "_arrivals_loader");
                if(loader != null) {
                  loader.remove();
                }
                new_list = createArrivalList(stop_arrival_data.arrivals, id);
                table.replaceChild(new_list, old_list);
            }
        }
    }
    xhr.send();
}

function refreshArrivalDivs(repeat = true) {
    let ms = getMonitoredStops();
    if(ms.length == 0)
      return false;

    let last_element = null;
    for (stop of ms) {
        let div = document.getElementById(stop + "_arrivals");
        if (div == null) {
            div = createArrivalDiv(stop)
            if(last_element == null) {
              arrival_cards.insertBefore(div, arrival_cards.firstChild);
            }
            else {
              arrival_cards.insertBefore(div, last_element.nextSibling);
            }
        }
        last_element = div;
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
    return true;
};


function getCardTemplate(resolve, reject) {
    let xhr = new XMLHttpRequest();
    let template = "";
    xhr.open('GET', api_host() + "/api/card_template");
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.responseText == "") {
                reject(xhr.statusText);
            }
            else {
                resolve(xhr.responseText);
            }
        }
    };
    xhr.send();
}

window.onload = function() {
  card_template_promise = new Promise(getCardTemplate);


  let default_cards = document.getElementsByClassName("arrival-card");

  let first_default_card = null;
  if(default_cards.length != 0) {
    let id = default_cards[0].getAttribute("data-naptan-id") + "_arrivals"
    first_default_card = document.getElementById(id);
  }

  for (let i = 0; i < default_cards.length; i++) {
    addMonitoredStop(default_cards[i].getAttribute("data-naptan-id"));
  }

  card_template_promise.then(function(t){
    card_template = t;
    if(!refreshArrivalDivs()) {
      setTimeout(() => $(stop_add_screen).modal('show'), 1500);
    }

    if(first_default_card != null) {
      window.scrollTo(0, first_default_card.offsetTop-40);
    }

    add_button.classList.remove("invisible");
  });
}
