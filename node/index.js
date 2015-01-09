//var REDIS_HOST = '50.116.1.193';
var REDIS_HOST = '127.0.0.1';

var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var socket_io_redis = require('socket.io-redis');
io.adapter(socket_io_redis({ host: REDIS_HOST, port: 6379 }));
var log = require('./logger')

var redis = require("redis"),
    client = redis.createClient(6379, REDIS_HOST);

client.on("error", function (err) {
    log.debug("Error " + err);
});


function getUsers(room, callback) {
    // get all users of the room
    client.smembers('rooms:' + room, function (err, resp) {

        // prepare a js list of dicts for socket.io
        client.mget(resp, function (err, resp) {

            log.debug(resp);

            var result = []

            debugger;

            for (var x in resp) {
                log.debug('***')
                log.debug(x);
                log.debug(resp[x]);
                result.push(JSON.parse(resp[x]));
            }

            callback(result);
        });
    });
}


io.on('connection', function (socket) {
    log.debug("===========================================");
    log.debug(">>> New socket was connected");

    socket.my_rooms = []

    socket.on('subscribe', function (data) {
        log.debug('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        var room = data.room;
        log.debug('joining room: user [' + data.user_id + '] room [' + room + ']');

        // join
        socket.join(room);

        // save id
        socket.user_id = data.user_id;

        // add user
        client.set('users:user_' + data.user_id, JSON.stringify(data.user), function (err, resp) {
            log.debug('adding user ' + data.user_id)

            // add user to room
            client.sadd('rooms:' + room, 'users:user_' + data.user.id, function (err, resp) {
                log.debug('adding user ' + data.user_id + ' to room ' + room)
                log.debug('222')
                getUsers(room, function (result) {
                    // update socket.io clients
                    io.to(room).emit('update_users', result, room)

                    socket.my_rooms.push(room);
                });
            });
        });
    });

    socket.on('unsubscribe', function (data) {
        log.debug("===========================================");
        log.debug('leaving room: user [' + data.user_id + '] room [' + data.room + ']');

        socket.leave(data.room);

        // delete user from the room
        client.srem('rooms:' + data.room, 'users:user_' + data.user_id, function (err, resp) {
            log.debug('deleted')

            log.debug('333')
            getUsers(data.room, function (result) {
                // update socket.io clients
                io.to(data.room).emit('update_users', result, data.room);
                socket.broadcast.emit('info', 'User: ' + data.user_id + ' has leave room ' + data.room);

                var idx = socket.my_rooms.indexOf(data.room);
                if (idx > -1) {
                    socket.my_rooms.splice(idx, 1);
                }
            });
        });
    });


    socket.on('update_my_info', function (data) {
        log.debug("===========================================");
        log.debug("Update My Info to: %j", {data: data}, {})

        client.set('users:user_' + data.id, JSON.stringify(data), function (err, resp) {
            for (var r in socket.my_rooms) {
                var room = socket.my_rooms[r]

                log.debug('update users in room ' + room + ' ...' + data.id)
                log.debug('444')
                getUsers(room, function (result) {
                    io.to(room).emit('update_users', result, room)
                });
            }
        });
    });


    socket.on('user_message', function (msg) {
        log.debug("===========================================");
        log.debug('== User message: %j', {msg: msg}, {})
        io.sockets.in(msg.room).emit('msg_to_room', msg);
    });

    socket.on('system_message', function (msg) {
        log.debug("===========================================");
        log.debug('== System message: %j', {msg: msg}, {})
        io.to(msg.room).emit('system_msg_to_room', msg);
    });

    socket.on('background_message', function (msg) {
        log.debug("===========================================");
        log.debug('== Background message: %j', {msg: msg}, {})
        io.sockets.in(msg.room).emit('background_msg_to_room', msg);
    });


    socket.on('disconnect', function () {
        log.debug("===========================================");
        log.debug('disconnect user [' + socket.user_id + ']');

        if (socket.user_id) {

            for (var r in socket.my_rooms) {
                var room = socket.my_rooms[r];
                client.srem('rooms:' + room, 'users:user_' + socket.user_id, function (err, resp) {
                    log.debug('deleted from room on disconnect')

                    log.debug('555 '+ room);
                    getUsers(room, function (result) {
                        log.debug(result)
                        // update socket.io clients
                        io.to(room).emit('update_users', result, room);
                    });
                });
            }

            socket.my_rooms=[]

            client.srem('users:user_' + socket.user_id, function (err, resp) {
                log.debug('user deleted on disconnect')
                socket.broadcast.emit('info', 'User: ' + socket.user_id + ' has disconnected');
            });
        } else {
            log.debug('Not joined socket was disconnected')
        }
    });
});


http.listen(3000, function () {
    log.debug('listening on *:3000');
});
