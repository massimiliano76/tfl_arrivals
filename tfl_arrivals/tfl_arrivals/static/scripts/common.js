
function api_host() {
    if (window.location.hostname == "localhost")
        return "http://localhost:5555";
    else
        return "http://" + window.location.hostname;
}