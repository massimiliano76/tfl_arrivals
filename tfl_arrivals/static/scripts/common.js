
function api_host() {
    if (window.location.hostname == "localhost")
        return "http://localhost:5000";
    else
        return "http://" + window.location.hostname;
}
