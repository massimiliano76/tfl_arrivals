const getMonitoredStops = (name) => {
    stops = JSON.parse(localStorage.getItem("monitored_stops"));
    return stops === null ? [] : stops
}

const deleteMonitoredStop = (name) => {
    let ms = getMonitoredStops(name)
    const idx = ms.indexOf(name);
    if (idx > -1) {
        ms.splice(idx, 1);
    }
    localStorage.setItem("monitored_stops", JSON.stringify(ms));
}

const addMonitoredStop = (name) => {
    let ms = getMonitoredStops(name)
    const idx = ms.indexOf(name);
    if (idx == -1) {
        ms.push(name)
        localStorage.setItem("monitored_stops", JSON.stringify(ms));
    }
}
