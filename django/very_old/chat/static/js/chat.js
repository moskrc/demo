$(function() {

    var socket;

    var scrollChatDown = function() {
        var objDiv = document.getElementById("messages");
        objDiv.scrollTop = objDiv.scrollHeight;
    }

    var scrollWidnowDown = function() {
        window.scrollBy(0, 10000);
    }

    var addItem = function(selector, item) {
        var template = $(selector).find('script[type="text/x-jquery-tmpl"]');
        template.tmpl(item).appendTo(selector);
        scrollChatDown()
    };

    var addMessage = function(data) {
        var d = new Date();
        data.time = $.map([d.getHours(), d.getMinutes(), d.getSeconds()],
                          function(s) {
                              s = String(s);
                              return (s.length == 1 ? '0' : '') + s;
                          }).join(':');

        data['message'] = data['message'].replace(/\r?\n|\r/g, "<br>");
        addItem('#messages', data);
    };

    var connected = function() {
        socket.subscribe('room-' + window.room);
    };

    var disconnected = function() {
        setTimeout(start, 1000);
    };

    var messaged = function(data) {
        switch (data.action) {
            case 'message':
                addMessage(data);
                break;
        }
    };

    var start = function() {
        
        if ($.browser.msie) {
            socket = new io.Socket('concierge.grape.ru', {
                port: 9000,
                transports: ['jsonp-polling', 'xhr-multipart', 'websocket',  'xhr-polling', 'websocket', 'flashsocket', 'htmlfile'],
                rememberTransport: false
            });
        } else {
            socket = new io.Socket('concierge.grape.ru', {
                port: 9000,
                transports: ['xhr-multipart', 'xhr-polling', 'websocket', 'flashsocket', 'htmlfile', 'jsonp-polling'],
                rememberTransport: false
            });
        }
        
        socket.connect();
        socket.on('connect', connected);
        socket.on('disconnect', disconnected);
        socket.on('message', messaged);
    };


    /////////////////////

    start();

    scrollChatDown();

    scrollWidnowDown();

    $("#new_message").keydown(function(e){
        // Enter was pressed without shift key
        if (e.keyCode == 13 && e.shiftKey)
        {
            // prevent default behavior
            $('.send_msg_form').submit();
            e.preventDefault();
        }
    });

    $('form.send_msg_form').submit(function() {

        var value = $('.send_msg_form input').val() || $('.send_msg_form textarea').val();

        if (value) {
            var data = {room: window.room, uid: window.uid, action: 'message', message: value, is_staff: window.is_staff};
            socket.send(data);
        }

        $('.send_msg_form textarea').val('').focus();
        $('.send_msg_form #new_message').val('').focus();

        return false;
    });

});
