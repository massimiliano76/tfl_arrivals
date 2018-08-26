
function api_host() {
    if (window.location.hostname == "localhost")
        return "http://localhost:5000";
    else if (window.location.hostname == "127.0.0.1")
        return "http://127.0.0.1:5000";
    else
        return "http://" + window.location.hostname;
}

function api_host_gcp() {
    if (window.location.hostname == "localhost")
        return "http://localhost:8080";
    else if (window.location.hostname == "127.0.0.1")
        return "http://127.0.0.1:8080";
    else
        return "https://arrivals-of-london.appspot.com";
}
