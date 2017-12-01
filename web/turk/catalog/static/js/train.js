
$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/train" + window.location.pathname);
    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        console.log('Message:' + data.log);
        var elem = document.createElement("p");
        elem.innerHTML = data.log;
        $('#train').append(elem);
    };
});