const setCookie = (name, value, days = 365, path = '/') => {
  const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString()
  document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=' + path
}

const getCookie = (name) => {
  return document.cookie.split('; ').reduce((r, v) => {
    const parts = v.split('=')
    return parts[0] === name ? decodeURIComponent(parts[1]) : r
  }, '')
}

const deleteCookie = (name, path) => {
  setCookie(name, '', -1, path)
}

const getMonitoredStopsFromCookie = (name) => {
    s = getCookie("monitored_stops");
    if (s.length == 0) 
        return []

    return s.split(",");
}

const deleteMonitoredStopFromCookie = (name) => {
    let ms = getMonitoredStopsFromCookie(name)    
    const idx = ms.indexOf(name);
    if (idx > -1) {
        ms.splice(idx, 1);
    }
    setCookie("monitored_stops", ms.join());
}

const addMonitoredStop = (name) => {
    let ms = getMonitoredStopsFromCookie(name)
    const idx = ms.indexOf(name);
    if (idx == -1) {
        ms.push(name)
        setCookie("monitored_stops", ms.join());
    }
}